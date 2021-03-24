from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from secrets import token_urlsafe
from datetime import timedelta

from math import exp
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
        self.create_data(1)
        #self.stdout.write('Finished creating dummy data for PSU \'%s\'.' % str(self.psu))


    def create_data(self, days, *, steps=15):
        """
        function to create the data
        """
        cTime = timezone.now().replace(hour=0, minute=randint(0,5), second=randint(0,59), microsecond=randint(0,999999)) - timedelta(days=days)
        #self.stdout.write('START TIME: %s' % str(cTime))

        # starting with temperature between -5 and 20 degrees
        cTemp = random() * 25 - 5
        # setting ari humidity static for now
        cAHum = 10
        # starting with ground humidity between 0 and 100
        cGHum = random() * 100
        # starting with 70 to 100 fill level
        cFLevel = random() * 30 + 70
        # starting with brightness betwenn 0 and 30 (midnight)
        cBright = random() * 30
        mins = 0
        
        while (timezone.now() - cTime) > timedelta():

            # write CSV-formated list for testing
            self.stdout.write('{};{:.6f};{:.6f};{:.6f};{:.6f};{:.6f}'.format(cTime.strftime("%d.%m.%y %H:%M:%S"), cTemp, cAHum, cGHum, cFLevel, cBright).replace('.',',').replace(',', '.', 2))
            
            mins += steps
            cTime = cTime + timedelta(minutes=steps, seconds=randint(0, 29), microseconds=randint(0,999999))

