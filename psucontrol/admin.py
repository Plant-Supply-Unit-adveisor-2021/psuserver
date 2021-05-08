from django.contrib import admin

from psucontrol.models import WateringParams, PSU, PendingPSU, DataMeasurement, PSUImage, WateringTask, CommunicationLogEntry, WateringDecision


# Register your models here.
@admin.register(WateringParams)
class WateringParamsAdmin(admin.ModelAdmin):
    model = WateringParams

    list_display = ['id', 'name', 'ground_humidity_goal', 'minimum_amount', 'maximum_amount', 'starting_amount']
    search_fields = ['id', 'name']


@admin.register(PSU)
class PSUAdmin(admin.ModelAdmin):
    model = PSU

    list_display = ['id', 'name', 'owner', 'watering_params', 'identity_key']
    list_filter = ['owner', 'watering_params', 'unauthorized_watering']
    search_fields = ['id', 'name', 'owner__email', 'owner__last_name', 'owner__first_name', 'watering_params__name', 'identity_key']


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


@admin.register(PSUImage)
class PSUImageAdmin(admin.ModelAdmin):
    model = PSUImage

    list_display = ['psu', 'timestamp', 'image']
    list_filter = ['psu']
    search_fields = ['psu__id', 'psu__name', 'psu__owner__email', 'psu__owner__last_name', 'psu__owner__first_name']


@admin.register(WateringTask)
class WateringTaskAdmin(admin.ModelAdmin):
    model = WateringTask

    list_display = ['id', 'timestamp', 'status', 'amount', 'psu']
    list_filter = ['psu', 'status']
    search_fields = ['psu__id', 'psu__name', 'psu__owner__email', 'psu__owner__last_name', 'psu__owner__first_name', 'status']


@admin.register(CommunicationLogEntry)
class CommunicationLogEntryAdmin(admin.ModelAdmin):
    model = CommunicationLogEntry

    list_display = ['timestamp', 'level', 'psu_identity_key', 'request_uri']
    list_filter = ['level', 'psu', 'request_uri']
    search_fields = ['psu__id', 'psu__name', 'psu__owner__email', 'psu__owner__last_name', 'psu__owner__first_name', 'level', 'request_uri', 'psu_identity_key']


@admin.register(WateringDecision)
class WateringDecisionAdmin(admin.ModelAdmin):
    model = WateringDecision

    list_display = ['timestamp', 'psu', 'amount', 'watering_params']
    list_filter = ['psu', 'watering_params']
    search_fields = ['psu__id', 'psu__name', 'psu__owner__email', 'psu__owner__last_name', 'psu__owner__first_name', 'watering_params__name']
