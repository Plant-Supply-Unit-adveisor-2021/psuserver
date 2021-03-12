from django.contrib import admin

from psucontrol.models import PSU, PendingPSU, DataMeasurement

# Register your models here.
@admin.register(PSU)
class PSUAdmin(admin.ModelAdmin):
    model = PSU

    list_display = ['id', 'name', 'owner', 'identity_key']
    search_fields = ['id', 'name', 'owner', 'identity_key']


@admin.register(PendingPSU)
class PendingPSUAdmin(admin.ModelAdmin):
    model = PendingPSU

    list_display = ['pairing_key', 'identity_key']
    search_fields = ['pairing_key', 'identity_key']


@admin.register(DataMeasurement)
class DataMeasurementAdmin(admin.ModelAdmin):
    model = DataMeasurement

    list_display = ['psu', 'timestamp', 'temperature', 'ground_humidity', 'brightness']
    search_fields = ['psu', 'temperature', 'ground_humidity', 'brightness']
