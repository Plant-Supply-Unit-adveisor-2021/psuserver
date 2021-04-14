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

        # get lease times
        minor_delta = get_timedelta(options['minor'])
        normal_delta = get_timedelta(options['normal'])
        major_delta = get_timedelta(options['major'])

        # print lease times to screen
        self.stdout.write('Lease time of minor log entries: {}'.format(str(minor_delta)))
        self.stdout.write('Lease time of normal log entries: {}'.format(str(normal_delta)))
        self.stdout.write('Lease time of major log entries: {}'.format(str(major_delta)))

        rm = 0
        for l in CommunicationLogEntry.objects.all():
            # check if log entry should be deleted
            if (l.level < 10 and minor_delta is not None and (timezone.now() - l.timestamp) > minor_delta) or \
               (10 <= l.level < 100 and normal_delta is not None and (timezone.now() - l.timestamp) > normal_delta) or \
               (l.level >= 100 and major_delta is not None and (timezone.now() - l.timestamp) > major_delta):
                l.delete()
                rm += 1
        
        self.stdout.write('Removed {} log entries.'.format(str(rm)))
