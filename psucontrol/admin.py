from django.contrib import admin

from psucontrol.models import PSU, DataMeasurement

# Register your models here.
@admin.register(PSU)
class PSUAdmin(admin.ModelAdmin):
    model = PSU

    list_display = ['id', 'name', 'owner']
    search_fields = ['id', 'name', 'owner']

@admin.register(DataMeasurement)
class DataMeasurementAdmin(admin.ModelAdmin):
    model = DataMeasurement

    list_display = ['psu', 'timestamp', 'temperature', 'ground_humidity', 'brightness']
    search_fields = ['psu', 'temperature', 'ground_humidity', 'brightness']
