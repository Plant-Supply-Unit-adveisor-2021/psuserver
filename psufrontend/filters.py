import django_filters

from psucontrol.models import *

class DataMeasurementFilter(django_filters.FilterSet):
	class Meta:
		model = DataMeasurement
		fields = '__all__'