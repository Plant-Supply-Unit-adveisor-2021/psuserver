from threading import Thread
from time import sleep

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

    def run(self):
        """
        this method is called when starting the Thread
        """
        sleep(10)
        print("Exited {}".format(self.name))
