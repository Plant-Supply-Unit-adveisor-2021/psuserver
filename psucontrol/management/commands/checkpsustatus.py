from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from psucontrol.models import PSU, DataMeasurement
from website.utils import get_timedelta


class Command(BaseCommand):
    """
    command to check whether all PSUs recently send data and if not notify people
    """
    help = 'Create more or less realistic dummy DataMeasurements'

    def add_arguments(self, parser):
        parser.add_argument('-a', '--admin', action='store_true', help='Notify admins')
        parser.add_argument('-p', '--psus', type=str, default='-1', help='Comma seperated list of psu ids to check. Defaults to all psus.')
        parser.add_argument('-t', '--time', type=str, default='4h',
                            help='Allowed offline time in format [num days]d[num hours]h[num minutes]m[num seconds]s for major level. Defaults to 4h')

    def handle(self, *args, **options):

        # get lease time
        max_delta = get_timedelta(options['time'])
        psu_ids = options['psus'].split(',')

        # get psus
        psus = []
        if psu_ids[0] == '-1':
            psus = PSU.objects.all()
        else:
            for id in psu_ids:
                try:
                    psus.append(PSU.objects.get(id=id))
                except PSU.DoesNotExist:
                    self.stdout.write('There is no psu with id {} registered.'.format(str(id)))

        # print lease time and mail to screen
        self.stdout.write('Allowed offline time: {}'.format(str(max_delta)))
        self.stdout.write('Mail used to send out mails: {}'.format(settings.DEFAULT_FROM_EMAIL))

        # check psus for last entry
        for psu in psus:
            last_entry = DataMeasurement.objects.filter(psu=psu).order_by('-timestamp').first()
            if last_entry is None:
                # message for no entry
                self.stdout.write('Last entry of {}: NONE'.format(str(psu)))
            else:
                delta = timezone.now() - last_entry.timestamp
                if delta > max_delta:
                    # message for last entry too long ago
                    self.stdout.write('Last entry of {}: {}, thats {} and too long ago'.format(str(psu), last_entry.timestamp.strftime('%d.%m.%Y %H:%M:%S'), str(delta)))
                else:
                    # message for everything is fine
                    self.stdout.write('Last entry of {}: {}, thats {} ago'.format(str(psu), last_entry.timestamp.strftime('%d.%m.%Y %H:%M:%S'), str(delta)))
