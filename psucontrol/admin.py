from django.contrib import admin

from psucontrol.models import PSU, PendingPSU, DataMeasurement, CommunicationLogEntry


# Register your models here.
@admin.register(PSU)
class PSUAdmin(admin.ModelAdmin):
    model = PSU

    list_display = ['id', 'name', 'owner', 'identity_key']
    search_fields = ['id', 'name', 'owner', 'identity_key']


@admin.register(PendingPSU)
class PendingPSUAdmin(admin.ModelAdmin):
    model = PendingPSU

    list_display = ['creation_time', 'pairing_key', 'identity_key']
    search_fields = ['pairing_key', 'identity_key']


@admin.register(DataMeasurement)
class DataMeasurementAdmin(admin.ModelAdmin):
    model = DataMeasurement

    list_display = ['psu', 'timestamp', 'temperature', 'air_humidity', 'ground_humidity', 'brightness', 'fill_level']
    list_filter = ['psu']
    search_fields = ['psu__id', 'psu__name', 'psu__owner__email', 'psu__owner__last_name', 'psu__owner__first_name']


@admin.register(CommunicationLogEntry)
class CommunicationLogEntryAdmin(admin.ModelAdmin):
    model = CommunicationLogEntry

    list_display = ['timestamp', 'level', 'psu', 'request_url']
    list_filter = ['level', 'psu', 'request_url']
    search_fields = ['psu__id', 'psu__name', 'psu__owner__email', 'psu__owner__last_name', 'psu__owner__first_name', 'level', 'request_url']
