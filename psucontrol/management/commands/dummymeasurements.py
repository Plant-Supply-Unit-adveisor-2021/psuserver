from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    """
    command to automatically create dummy test data
    """
    help = 'Create more or less realistic dummy DataMeasurements'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Creating dummy data. This might take a while ...')