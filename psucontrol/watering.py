from threading import Thread
from datetime import timedelta

from psucontrol.models import WateringTask, DataMeasurement, WateringDecision

class CalculateWatering(Thread):
    """
    class to handling the calculation for the amount which is needed to keep the plant alive
    the water amount is calculated in milliliters
    these threads are always open after a PSU sent a new data measurement
    """

    def __init__(self, psu):
        super().__init__()
        self.name = "Watering Calculation for {}".format(str(psu))
        # Storing the PSU for which the need should be calculated
        self.psu = psu


    def create_task(self, amount):
        """
        function to create the corresponding watering task and sort out old ones
        """
        if self.psu.unauthorized_watering:
            # no authorization necessary -> set status to authrozied and also search for authrozied old tasks
            status_to_cancel = [0, 5]
            task = WateringTask(psu=self.psu, amount=amount, status=5)
        else:
            # do not cancel authorized tasks
            status_to_cancel = [0]
            task = WateringTask(psu=self.psu, amount=amount, status=0)
            
        # cancel old tasks
        old_tasks = WateringTask.objects.filter(psu=self.psu, status__in=status_to_cancel)
        for ot in old_tasks:
            ot.status = -10
            ot.save()

        task.save()

    def crunch_data(self):
        """
        returns: amount to be used 
        """
        dms = DataMeasurement.objects.filter(psu=self.psu)

        # seatch for lastest ground_humidity information
        current_dm = None
        for dm in dms:
            if not dm.ground_humidity is None:
                current_dm = dm
                break

        if current_dm is None:
            # no data -> do not water plant
            WateringDecision.objects.create(psu=self.psu, watering_params=self.psu.watering_params, amount=0,
                                            info="No measurements with ground humidity found.")
            return 0

        if (current_dm.ground_humidity >= self.psu.watering_params.ground_humidity_goal or 
            (not current_dm.brightness is None and current_dm.brightness <= self.psu.watering_params.light_level_limit)):
            # no need to check watering because plant is happy now or too dark to water plant now
            WateringDecision.objects.create(psu=self.psu, watering_params=self.psu.watering_params, amount=0,
                                            info="Either plant happy or too dark.\nCurrent: {}".format(current_dm))
            return 0

        last_task = WateringTask.objects.filter(psu=self.psu, status=20).first()
        if last_task is None:
            WateringDecision.objects.create(psu=self.psu, watering_params=self.psu.watering_params, amount=self.psu.watering_params.starting_amount,
                                            info="No Task found.\nCurrent: {}".format(current_dm))
            return self.psu.watering_params.starting_amount

        after_dm = current_dm
        prev_dm = current_dm
        for dm in dms:
            if (last_task.timestamp_execution - dm.timestamp) >= timedelta() and not dm.ground_humidity is None:
                # current dm older than last watering
                prev_dm = dm
                break
            elif not dm.ground_humidity is None:
                # store the timestamp as candidate for after
                after_dm = dm

        # got for a proportional approach for now
        delta_ghum_last = after_dm.ground_humidity - prev_dm.ground_humidity
        delta_ghum_now = self.psu.watering_params.ground_humidity_goal - current_dm.ground_humidity

        if delta_ghum_last <= 0 and prev_dm != current_dm:
            # psu sending data obviously but something went wrong -> use starting amount
            WateringDecision.objects.create(psu=self.psu, watering_params=self.psu.watering_params, amount=self.psu.watering_params.starting_amount,
                                            info="delta_ghum_last <= 0.\nCurrent: {}\nPrev: {}\nAfter: {}\nLast: {}".format(current_dm, prev_dm, after_dm, last_task))
            return self.psu.watering_params.starting_amount
        elif delta_ghum_last == 0:
            # probably no data there to use
            WateringDecision.objects.create(psu=self.psu, watering_params=self.psu.watering_params, amount=0,
                                            info="delta_ghum_last == 0 (no new measurements?)\nCurrent: {}\nPrev: {}\nAfter: {}\nLast: {}".format(current_dm, prev_dm, after_dm, last_task))
            return 0

        amount = int( delta_ghum_now / delta_ghum_last * last_task.amount )

        # check if minimum requirement is fullfilled
        if self.psu.watering_params.minimum_amount <= amount <= self.psu.watering_params.maximum_amount:
            WateringDecision.objects.create(psu=self.psu, watering_params=self.psu.watering_params, amount=amount,
                                            info="Everything is looking fine.\nCurrent: {}\nPrev: {}\nAfter: {}\nLast: {}".format(current_dm, prev_dm, after_dm, last_task))
            return amount
        elif amount >= self.psu.watering_params.maximum_amount:
            # water only with maximum amount
            WateringDecision.objects.create(psu=self.psu, watering_params=self.psu.watering_params, amount=self.psu.watering_params.maximum_amount,
                                            info="Overshoot\nCurrent: {}\nPrev: {}\nAfter: {}\nLast: {}".format(current_dm, prev_dm, after_dm, last_task))
            return self.psu.watering_params.maximum_amount
        else:
            WateringDecision.objects.create(psu=self.psu, watering_params=self.psu.watering_params, amount=0,
                                            info="Not worth sending out.\nCurrent: {}\nPrev: {}\nAfter: {}\nLast: {}".format(current_dm, prev_dm, after_dm, last_task))
            return 0

        
    def run(self):
        """
        this method is called when starting the thread
        """
        print("Started {}".format(self.name))

        params = self.psu.watering_params

        if (WateringTask.objects.filter(psu=self.psu).count() > 0 and
            (DataMeasurement.objects.filter(psu=self.psu).first().timestamp - WateringTask.objects.filter(psu=self.psu).first().timestamp) <= timedelta()):
            # newest WateringTask created after DataMeasurement
            print("No new data for doing another calculation.")

        elif params is None:
            # check if there is an algorithm specified
            print("No algorithm paramters specified -> will not perform calculation")
        
        else:
            # run calculation
            print("Algrothim parameters to be used {}".format(str(params)))
            # Testing purposes create watering task without calculation
            amount = self.crunch_data()
            if amount > 0:
                self.create_task(amount)
        
        print("Exited {}".format(self.name))

    
    def crunch_data_dry(self):
        """
        function which returns the amount but does not do anything in the database
        returns: amount to be used
        """
        dms = DataMeasurement.objects.filter(psu=self.psu)

        # seatch for lastest ground_humidity information
        current_dm = None
        for dm in dms:
            if not dm.ground_humidity is None:
                current_dm = dm
                break

        if current_dm is None:
            # no data -> do not water plant
            return 0

        if (current_dm.ground_humidity >= self.psu.watering_params.ground_humidity_goal or 
            (not current_dm.brightness is None and current_dm.brightness <= self.psu.watering_params.light_level_limit)):
            # no need to check watering because plant is happy now or too dark to water plant now
            return 0

        last_task = WateringTask.objects.filter(psu=self.psu, status=20).first()
        if last_task is None:
            return self.psu.watering_params.starting_amount

        after_dm = current_dm
        prev_dm = current_dm
        for dm in dms:
            if (last_task.timestamp_execution - dm.timestamp) >= timedelta() and not dm.ground_humidity is None:
                # current dm older than last watering
                prev_dm = dm
                break
            elif not dm.ground_humidity is None:
                # store the timestamp as candidate for after
                after_dm = dm

        # got for a proportional approach for now
        delta_ghum_last = after_dm.ground_humidity - prev_dm.ground_humidity
        delta_ghum_now = self.psu.watering_params.ground_humidity_goal - current_dm.ground_humidity

        if delta_ghum_last <= 0 and prev_dm != current_dm:
            # psu sending data obviously but something went wrong -> use starting amount
            return self.psu.watering_params.starting_amount
        elif delta_ghum_last == 0:
            # probably no data there to use
            return 0

        amount = int( delta_ghum_now / delta_ghum_last * last_task.amount )

        # check if minimum requirement is fullfilled
        if self.psu.watering_params.minimum_amount <= amount <= self.psu.watering_params.maximum_amount:
            return amount
        elif amount >= self.psu.watering_params.maximum_amount:
            # water only with maximum amount
            return self.psu.watering_params.maximum_amount
        else:
            return 0
