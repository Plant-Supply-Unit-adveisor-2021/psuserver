from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from secrets import token_urlsafe
from datetime import timedelta

from math import exp, log
from random import random, randint

from psucontrol.models import PSU, DataMeasurement
from website.utils import getTestUser


class Command(BaseCommand):
    """
    command to automatically create dummy test data
    """
    help = 'Create more or less realistic dummy DataMeasurements'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--PSU', type=int, help='ID of the PSU for which the data should be created.')
        parser.add_argument('-c', '--create', action='store_true', help='Create a new PSU. Overwrites -p/--PSU.')

    @transaction.atomic
    def handle(self, *args, **options):
        
        # create a new PSU if create option was given
        if options['create']:
            self.psu = PSU.objects.create(name='TEST PSU', identity_key=token_urlsafe(96), public_rsa_key=token_urlsafe(96), owner=getTestUser())

        # try to get the PSU specified through -p / --PSU
        elif options['PSU']:
            try:
                self.psu = PSU.objects.get(id=options['PSU'])
            except PSU.DoesNotExist as e:
                self.stdout.write(self.style.ERROR('Error: There is no PSU with the ID %s in the current database.' % options['PSU']))
                return

        else:
            self.stdout.write(self.style.ERROR('Error: You have to use either the -c option to create a new PSU or the -p option to specify one.'))
            return

        #self.stdout.write('Started creating dummy data for PSU \'%s\'. This might take a while ...' % str(self.psu))
        self.create_data(2)
        #self.stdout.write('Finished creating dummy data for PSU \'%s\'.' % str(self.psu))


    def create_data(self, days, *, step=15):
        """
        function to create the data
        """
        cTime = timezone.now().replace(hour=0, minute=randint(0,5), second=randint(0,59), microsecond=randint(0,999999)) - timedelta(days=days)
        #self.stdout.write('START TIME: %s' % str(cTime))

        # starting with temperature between 5 and 20 degrees
        cTemp = random() * 15 + 5
        tempTrend = random() * 0.2 - 0.1
        # setting ari humidity static for now
        cAHum = 10
        # starting with ground humidity between 0 and 100
        cGHum = random()
        # starting with 70 to 100 fill level
        cFLevel = random() * 0.3 + 0.7
        # starting with brightness betwenn 0 and 30 (midnight)
        cBright = random() * 30
        counter = 0
        
        while (timezone.now() - cTime) > timedelta():
            
            # logic for the tempreature
            if cTime.hour == 3 and cTime + timedelta(minutes=step) == 4:
                tempTrend = random() * 0.2 - 0.1
            if cTime.hour < 4 or cTime.hour > 19:
                # let temperatures sink
                cTemp += (-random() * 4 + 0.5 + tempTrend) * step / 60
            elif (cTime.hour >= 4 and cTime.hour < 6) or (cTime.hour > 17 and cTime.hour <= 19):
                # let temperatures sink just a little
                cTemp += (-random() * 2 + 0.25 + tempTrend) * step / 60
            elif (cTime.hour >= 6 and cTime.hour < 8) or (cTime.hour > 15 and cTime.hour <= 17):
                # let temerature raise just a little
                cTemp += (random() * 2 - 0.25 + tempTrend) * step / 60
            else:
                # let temerature raise
                cTemp += (random() * 4 - 0.5 + tempTrend) * step / 60

            # logic for ground humidity and the watering of the plant
            if cTemp <= 10:
                parm = 900
            else:
                parm = 1020 - 6*abs(cTemp) ** 1.3
            cGHum = exp((log(cGHum) * parm -step) / parm)
            if random() < (cGHum + 1) ** -20:
                # watering of the plant
                cFLevel -= (1 - cGHum)/8
                cGHum = random() * 0.1 + 0.8

            # write CSV-formated list for testing
            self.stdout.write('{};{:.6f};{:.6f};{:.6f};{:.6f};{:.6f}'.format(cTime.strftime("%d.%m.%y %H:%M:%S"), cTemp, cAHum, cGHum * 100, cFLevel * 100, cBright).replace('.',',').replace(',', '.', 2))
            
            counter += step
            cTime = cTime + timedelta(minutes=step, seconds=randint(0, 29), microseconds=randint(0,999999))
