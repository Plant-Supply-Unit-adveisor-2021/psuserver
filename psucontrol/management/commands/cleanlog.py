from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from datetime import timedelta
import re

from psucontrol.models import CommunicationLogEntry

def get_timedelta(string):
    """
    convert a string in the format [num days]d[num hours]h[num minutes]m[num seconds]s
    if not possible return None
    """
    regex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
    parms = regex.match(string)
    
    args = dict()
    for (name, parm) in parms.groupdict().items():
        if parm:
            args[name] = int(parm)
    if len(args) < 1:
        return None
    return timedelta(**args)


class Command(BaseCommand):
    """
    command to clean log entries according to given lease times
    """
    help = 'Create more or less realistic dummy DataMeasurements'

    def add_arguments(self, parser):
        parser.add_argument('-m', '--minor', type=str, default='NONE',
                            help='Lease time in format [num days]d[num hours]h[num minutes]m[num seconds]s for minor level. Defaults to None')
        parser.add_argument('-n', '--normal', type=str, default='NONE',
                            help='Lease time in format [num days]d[num hours]h[num minutes]m[num seconds]s for normal level. Defaults to None')
        parser.add_argument('-M', '--major', type=str, default='NONE',
                            help='Lease time in format [num days]d[num hours]h[num minutes]m[num seconds]s for major level. Defaults to None')

    @transaction.atomic
    def handle(self, *args, **options):
        minor_delta = get_timedelta(options['minor'])
        normal_delta = get_timedelta(options['normal'])
        major_delta = get_timedelta(options['major'])

        self.stdout.write('Lease time of minor log entries: {}'.format(str(minor_delta)))
        self.stdout.write('Lease time of normal log entries: {}'.format(str(normal_delta)))
        self.stdout.write('Lease time of major log entries: {}'.format(str(major_delta)))
