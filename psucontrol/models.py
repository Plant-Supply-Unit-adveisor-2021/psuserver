from django.db import models
from django.utils.translation import ugettext_lazy as _

from authentication.models import User

# Create your models here.

class PSU(models.Model):
    """
    model representing a Plant Supply Unit
    This model holds the authentication data, user permissions and the name of the unit.
    """
    # id of the PSUs
    id = models.AutoField(primary_key=True)

    # name decribing the PSU
    name = models.CharField(_('name'), max_length=128)

    # authentication of the PSU
    identity_key = models.CharField(_('identity key'), max_length=128, unique=True)
    public_rsa_key = models.CharField(_('public rsa key'), max_length=451, unique=True)
    current_challenge = models.CharField(_('current challenge token'), max_length=128, blank=True)

    # ownership of the PSU
    owner = models.ForeignKey(User, models.PROTECT, verbose_name=_('owner'), related_name='owner')
    permitted_users = models.ManyToManyField(User, verbose_name=_('permitted users'), related_name='permitted_user', blank=True)

    def __str__(self):
        return '{:02d} - {}  --  {}'.format(self.id, self.name, self.owner)

    class Meta:
        verbose_name = _('Plant Supply Unit')
        verbose_name_plural = _('Plant Supply Units')
        ordering = ['id']


class PendingPSU(models.Model):
    """
    model representing a Plant Supply Unit which is waiting to be set up
    Create when a PSU makes first contact with the server
    """
    # authentication of the PSU identity and pairing key are created by the server
    identity_key = models.CharField(_('identity key'), max_length=128, unique=True)
    # generated by the PSU and handed over during registration process
    public_rsa_key = models.CharField(_('public rsa key'), max_length=451, unique=True)
    # only purpose of this key is to allow easy identification of psu in setup process
    pairing_key = models.CharField(_('pairing key'), max_length=6, unique=True)

    # creation time to handle removal of old pending psus
    creation_time = models.DateTimeField(_('creation time'), auto_now_add=True)

    class Meta:
        verbose_name = _('Pending Plant Supply Unit')
        verbose_name_plural = _('Pending Plant Supply Units')
        ordering = ['-creation_time']


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
    air_humidity = models.FloatField(_('air humidity'))
    ground_humidity = models.FloatField(_('ground humidity'))
    brightness = models.FloatField(_('brightness'))
    fill_level = models.FloatField(_('fill level'))

    def __str__(self):
        return '{} - {:02}.{:02}.{:04} {:02}:{:02}'.format(self.psu, self.timestamp.day, self.timestamp.month, self.timestamp.year, self.timestamp.hour, self.timestamp.minute)

    class Meta:
        verbose_name = _('Data Measurement')
        verbose_name_plural = _('Data Measurements')
        ordering = ['-timestamp', 'psu']
