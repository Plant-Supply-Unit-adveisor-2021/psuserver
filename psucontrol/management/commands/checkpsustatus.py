from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _

from psucontrol.models import PSU, DataMeasurement
from website.utils import get_timedelta


class MailingHandler():
    """
    class to collect messages for one user and send them out all at once
    """

    def __init__(self, user, psu, last_entry):
        self.user = user
        self.reports = []
        self.add_report(user, psu, last_entry)


    def add_report(self, user, psu, last_entry):
        """
        checks user and adds report if user is equal
        returns: true if user == self.user
        """
        if user == self.user:
            self.reports.append( (psu, last_entry) )
            return True
        return False


    def send_messages(self):
        msg = _('Hello ') + self.user.first_name + ', \n'
        msg += _('we care about your plants and therefore we want to inform you that the following plant supply unit(s) have not sent any data to our servers recently')
        msg += ': \n\n'

        for p in self.reports:
            msg += '  - {}'.format(p[0].name) + _(' sent no data since ')
            msg += p[1].timestamp.strftime('%d.%m.%Y %H:%M:%S') + '.\n'

        msg += '\n'
        msg += _('Please have a look at these units and check whether they are connected to the internet. \nYour Team Plant Supply Unit')
        return msg


class Command(BaseCommand):
    """
    command to check whether all PSUs recently send data and if not notify people
    """

    help = 'Create more or less realistic dummy DataMeasurements'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mailinger_handler = []
        self.options = dict()


    def add_arguments(self, parser):
        parser.add_argument('-a', '--admin', action='store_true', help='Notify admins')
        parser.add_argument('-p', '--psus', type=str, default='-1', help='Comma seperated list of psu ids to check. Defaults to all psus.')
        parser.add_argument('-t', '--time', type=str, default='4h',
                            help='Allowed offline time in format [num days]d[num hours]h[num minutes]m[num seconds]s for major level. Defaults to 4h')


    def get_psus(self):
        """
        returns: array with all PSUs which should be checked
        """
        psu_ids = self.options['psus'].split(',')

        # get psus
        psus = []
        if psu_ids[0] == '-1':
            # default -> use all PSUs
            psus = PSU.objects.all()
        else:
            # try getting all selected PSUs
            for id in psu_ids:
                try:
                    psus.append(PSU.objects.get(id=id))
                except PSU.DoesNotExist:
                    # log that PSU could not be found
                    self.stdout.write('There is no psu with id {} registered.'.format(str(id)))
        return psus


    def add_reports(self, psu, last_entry):
        """
        creates all reports needed
        """
        # for now just using owner
        users = [psu.owner]
        for u in users:
            found = False
            for h in self.mailinger_handler:
                if h.add_report(u, psu, last_entry):
                    found = True
                    break
            if not found:
                self.mailinger_handler.append(MailingHandler(u, psu, last_entry))


    def handle(self, *args, **options):
        """
        method called when command is called
        """
        self.options = options
        # get lease time
        max_delta = get_timedelta(options['time'])

        # print lease time and mail to screen
        self.stdout.write('Current time: {}'.format(timezone.now().strftime('%d.%m.%Y %H:%M:%S')))
        self.stdout.write('Allowed offline time: {}'.format(str(max_delta)))
        self.stdout.write('Mail used to send out mails: {}'.format(settings.DEFAULT_FROM_EMAIL))

        # check psus for last entry
        for psu in self.get_psus():
            last_entry = DataMeasurement.objects.filter(psu=psu).order_by('-timestamp').first()
            if last_entry is None:
                # message for no entry just in logs because the PSU obviously never worked
                self.stdout.write('Last entry of {}: NONE'.format(str(psu)))
            else:
                delta = timezone.now() - last_entry.timestamp
                if delta > max_delta:
                    # message for last entry too long ago
                    self.add_reports(psu, last_entry)
                    self.stdout.write('Last entry of {}: {}, thats {} and too long ago'.format(str(psu), last_entry.timestamp.strftime('%d.%m.%Y %H:%M:%S'), str(delta)))
                else:
                    # message for everything is fine
                    self.stdout.write('Last entry of {}: {}, thats {} ago'.format(str(psu), last_entry.timestamp.strftime('%d.%m.%Y %H:%M:%S'), str(delta)))

        for h in self.mailinger_handler:
            self.stdout.write(h.send_messages())
