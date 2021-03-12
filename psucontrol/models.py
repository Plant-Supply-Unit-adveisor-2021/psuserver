from django.db import models
from django.utils.translation import ugettext_lazy as _

from authentification.models import User

# Create your models here.

class PSU(models.Model):
    """
    model representing a Plant Supply Unit
    This model holds the authentification data, user permissions and the name of the unit.
    """
    # id of the PSUs
    id = models.AutoField(primary_key=True)

    # name decribing the PSU
    name = models.CharField(_('name'), max_length=128)

    # authentification of the PSU
    identity_key = models.CharField(_('identity key'), max_length=128, unique=True)

    # ownership of the PSU
    owner = models.ForeignKey(User, models.PROTECT, verbose_name=_('owner'), related_name='owner', null=True, blank=True)
    permitted_users = models.ManyToManyField(User, verbose_name=_('permitted users'), related_name='permitted_user', blank=True)

    def __str__(self):
        return '{:02d} - {}'.format(self.id, self.name)

    class Meta:
        verbose_name = _('Plant Supply Unit')
        verbose_name_plural = _('Plant Supply Units')
        ordering = ['id']

class DataMeasurement(models.Model):
    """
    model to store the measurement data of the PSUs
    """

    # field for storing the source psu of the data
    psu = models.ForeignKey(PSU, models.CASCADE, verbose_name=_('Plant Supply Unit'))

    # field storing the time stamp
    timestamp = models.DateTimeField(_('timestamp'))

    # for testing purposes only a few testing fields
    temperature = models.FloatField(_('temperature'))
    ground_humidity = models.FloatField(_('ground humidity'))
    brightness = models.FloatField(_('brightness'))

    def __str__(self):
        return '{} - {:02}.{:02}.{:04} {:02}:{:02}'.format(self.psu, self.timestamp.day, self.timestamp.month, self.timestamp.year, self.timestamp.hour, self.timestamp.minute)

    class Meta:
        verbose_name = _('Data Measurement')
        verbose_name_plural = _('Data Measurements')
        ordering = ['-timestamp', 'psu']
