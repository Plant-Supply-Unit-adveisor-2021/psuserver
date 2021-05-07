from threading import Thread
from datetime import timedelta

from psucontrol.models import WateringTask, DataMeasurement

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
            # self.create_task(-1)
        
        print("Exited {}".format(self.name))
