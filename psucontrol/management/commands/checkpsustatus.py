from django.core.management.base import BaseCommand
from django.utils import timezone

from psucontrol.models import DataMeasurement
from website.utils import get_timedelta


class Command(BaseCommand):
    """
    command to check whether all PSUs recently send data and if not notify people
    """
    help = 'Create more or less realistic dummy DataMeasurements'

    def add_arguments(self, parser):
        parser.add_argument('-a', '--admin', action='store_true', help='Notify admins')
        parser.add_argument('-t', '--time', type=str, default='4h',
                            help='Allowed offline time in format [num days]d[num hours]h[num minutes]m[num seconds]s for major level. Defaults to 4h')

    def handle(self, *args, **options):

        # get lease times
        delta = get_timedelta(options['time'])

        # print lease times to screen
        self.stdout.write('Allowed offline time: {}'.format(str(delta)))