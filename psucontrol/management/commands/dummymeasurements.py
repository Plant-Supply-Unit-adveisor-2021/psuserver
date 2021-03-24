from django.core.management.base import BaseCommand
from django.db import transaction

from secrets import token_urlsafe

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
            psu = PSU.objects.create(name='TEST PSU', identity_key=token_urlsafe(96), public_rsa_key=token_urlsafe(96), owner=getTestUser())

        # try to get the PSU specified through -p / --PSU
        elif options['PSU']:
            try:
                psu = PSU.objects.get(id=options['PSU'])
            except PSU.DoesNotExist as e:
                self.stdout.write(self.style.ERROR('Error: There is no PSU with the ID %s in the current database.' % options['PSU']))
                return

        else:
            self.stdout.write(self.style.ERROR('Error: You have to use either the -c option to create a new PSU or the -p option to specify one.'))
            return

        self.stdout.write('Started creating dummy data for PSU \'%s\'. This might take a while ...' % str(psu))