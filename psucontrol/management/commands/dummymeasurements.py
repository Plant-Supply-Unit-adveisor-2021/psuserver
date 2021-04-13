from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from secrets import token_urlsafe
from datetime import timedelta

from math import log
from random import random, randint

from psucontrol.models import PSU, DataMeasurement
from website.utils import get_test_user


class Command(BaseCommand):
    """
    command to automatically create dummy test data
    """
    help = 'Create more or less realistic dummy DataMeasurements'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--PSU', type=int, help='ID of the PSU for which the data should be created.')
        parser.add_argument('-c', '--create', action='store_true', help='Create a new PSU. Overwrites -p/--PSU.')
        parser.add_argument('-d', '--days', type=int, default=2,
                            help='Number of days in the past for which dummy data should be created. Defaults to 2.')
        parser.add_argument('-u', '--upcoming', type=int, default=3,
                            help='Number of upcoming hours for which dummy data should already be created. Defaults to 3.')
        parser.add_argument('-s', '--step', type=int, default=15,
                            help='Number of minutes between measurements. Defaults to 15.')

    @transaction.atomic
    def handle(self, *args, **options):

        # create a new PSU if create option was given
        if options['create']:
            self.psu = PSU.objects.create(name='TEST PSU', identity_key=token_urlsafe(96),
                                          public_rsa_key=token_urlsafe(96), owner=get_test_user())

        # try to get the PSU specified through -p / --PSU
        elif options['PSU']:
            try:
                self.psu = PSU.objects.get(id=options['PSU'])
            except PSU.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR('Error: There is no PSU with the ID %s in the current database.' % options['PSU']))
                return

        else:
            self.stdout.write(self.style.ERROR(
                'Error: You have to use either the -c option to create a new PSU or the -p option to specify one.'))
            return

        self.stdout.write('Started creating dummy data for PSU \'%s\'. This might take a while ...' % str(self.psu))
        self.create_data(options['days'], options['upcoming'], options['step'])
        self.stdout.write('Finished creating dummy data for PSU \'%s\'.' % str(self.psu))

    @transaction.atomic
    def create_data(self, days, upcoming_hours, step):
        """
        function to create the data
        """
        time = timezone.now().replace(hour=0, minute=randint(0, 5), second=randint(0, 59),
                                      microsecond=randint(0, 999999)) - timedelta(days=days)
        self.stdout.write('START TIME: %s' % str(time))

        # starting with temperature between 5 and 20 degrees
        temp = random() * 15 + 5
        temp_trend = random() * 0.2 - 0.1
        # setting air humidity between 0.25 and 0.75
        air_hum = random() * 0.5 + 0.25
        # starting with ground humidity between 0 and 100
        ground_hum = random()
        # starting with 70 to 100 fill level
        fill_level = random() * 0.3 + 0.7
        # starting with brightness 0 (midnight)
        bright = 0

        while (timezone.now() - time) > timedelta(hours=-upcoming_hours):

            # logic for the temperature
            if time.hour == 3 and time + timedelta(minutes=step) == 4:
                temp_trend = random() * 0.2 - 0.1
            if time.hour < 4 or time.hour > 19:
                # let temperature sink
                temp += (-random() * 4 + 0.5 + temp_trend) * step / 60
            elif (4 <= time.hour < 6) or (17 < time.hour <= 19):
                # let temperature sink just a little
                temp += (-random() * 2 + 0.25 + temp_trend) * step / 60
            elif (6 <= time.hour < 8) or (15 < time.hour <= 17):
                # let temperature raise just a little
                temp += (random() * 2 - 0.25 + temp_trend) * step / 60
            else:
                # let temperature raise
                temp += (random() * 4 - 0.5 + temp_trend) * step / 60

            # logic for the air humidity
            air_hum = max(min(air_hum + (temp - 15) * 0.002 * step / 60, 1), 0)

            # logic for the brightness
            if time.hour < 6 or time.hour > 20:
                # set the brightness to 0 quickly
                bright = max(bright - random() * 0.3 * step / 60, 0)
            elif 6 <= time.hour < 9:
                # let brightness raise
                bright = min(bright + random() * 0.6 * step / 60, 1)
            elif 18 <= time.hour < 21:
                # let brightness fall
                bright = max(bright - random() * 0.65 * step / 60, 0)
            else:
                # hover brightness around 1 but max 1
                bright = min(bright + (random() * 0.25 - 0.125) * step / 60, 1)

            # logic for ground humidity and the watering of the plant
            if temp <= 10:
                parm = 900
            else:
                parm = 1020 - 6 * abs(temp) ** 1.3
            ground_hum = 3.5 ** ((log(ground_hum, 3.5) * parm - step) / parm)
            if random() < (ground_hum + 1) ** -20:
                # watering of the plant
                fill_level = max(fill_level - (1 - ground_hum) / 8, 0)
                ground_hum = random() * 0.1 + 0.8

            # write CSV-formatted list for testing
            # self.stdout.write(  '{};{:.6f};{:.6f};{:.6f};{:.6f};{:.6f}'
            #                    .format(time.strftime("%d.%m.%y %H:%M:%S"),
            #                    addFail(temp, -10, 40, 1), addFail(air_hum*100, 0, 100, 2), addFail(ground_hum*100, 0, 100, 3), addFail(fill_level*100, 0, 100, 1.5), addFail(bright*100, 0, 100, 3))
            #                    .replace('.',',').replace(',', '.', 2))

            # create new DataMeasurement
            DataMeasurement.objects.create(psu=self.psu, timestamp=time, temperature=add_fail(temp, -10, 40, 1),
                                           air_humidity=add_fail(air_hum * 100, 0, 100, 2),
                                           ground_humidity=add_fail(ground_hum * 100, 0, 100, 3),
                                           fill_level=add_fail(fill_level * 100, 0, 100, 1.5),
                                           brightness=add_fail(bright * 100, 0, 100, 3))

            time = time + timedelta(minutes=step, seconds=randint(0, 29), microseconds=randint(0, 999999))


def add_fail(value, _min, _max, failure):
    return min(_max, max(_min, value + random() * failure - failure / 2))
