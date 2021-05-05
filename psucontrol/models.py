import os

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from authentication.models import User


# Create your models here.

class PSU(models.Model):
    """
    model representing a Plant Supply Unit
    This model holds the authentication data, user permissions and the name of the unit.
    """
    # id of the PSUs
    id = models.BigAutoField(primary_key=True)

    # name describing the PSU
    name = models.CharField(_('name'), max_length=128)

    # authentication of the PSU
    identity_key = models.CharField(_('identity key'), max_length=128, unique=True)
    public_rsa_key = models.TextField(_('public rsa key'), unique=True)
    current_challenge = models.CharField(_('current challenge token'), max_length=128, blank=True)

    # ownership of the PSU
    owner = models.ForeignKey(User, models.PROTECT, verbose_name=_('owner'), related_name='owner')
    permitted_users = models.ManyToManyField(User, verbose_name=_('permitted users'), related_name='permitted_user',
                                             blank=True)

    def __str__(self):
        return '{:02d} - {} ({})'.format(self.id, self.name, self.owner)

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
    public_rsa_key = models.TextField(_('public rsa key'), unique=True)
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

    # field storing the timestamp
    timestamp = models.DateTimeField(_('timestamp'))

    # data which is measured by a PSU
    temperature = models.FloatField(_('temperature'))
    air_humidity = models.FloatField(_('air humidity'))
    ground_humidity = models.FloatField(_('ground humidity'))
    brightness = models.FloatField(_('brightness'))
    fill_level = models.FloatField(_('fill level'))

    def __str__(self):
        return 'DM {} - {}'.format(self.psu, self.timestamp.strftime('%d.%m.%Y %H:%M:%S'))

    class Meta:
        verbose_name = _('Data Measurement')
        verbose_name_plural = _('Data Measurements')
        ordering = ['-timestamp', 'psu']
        unique_together = ['psu', 'timestamp']


def upload_image_path(instance, filename):
    return 'psufeed/{}/{}{}'.format(instance.psu.id, instance.timestamp.strftime('%Y-%m-%d_%H-%M-%S'), os.path.splitext(filename)[1])


class PSUImage(models.Model):
    """
    model for holding an image which was upload by a PSU
    """
    # field for storing the source psu of the image
    psu = models.ForeignKey(PSU, models.CASCADE, verbose_name=_('Plant Supply Unit'))

    # field storing the timestamp
    timestamp = models.DateTimeField(_('timestamp'))

    # field for storing the image
    image = models.ImageField(upload_to=upload_image_path, storage=settings.SECURE_MEDIA_STORAGE,verbose_name=_('image'))

    def __str__(self):
        return 'IMG {} - {}'.format(self.psu, self.timestamp.strftime('%d.%m.%Y %H:%M:%S'))

    class Meta:
        verbose_name = _('PSU Image')
        verbose_name_plural = _('PSU Images')
        ordering = ['-timestamp', 'psu']
        unique_together = ['psu', 'timestamp']


@receiver(models.signals.post_delete, sender=PSUImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `PSUImage` object is deleted.
    """
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)

@receiver(models.signals.pre_save, sender=PSUImage)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `PSUImage` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = PSUImage.objects.get(pk=instance.pk).image
    except PSUImage.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file and os.path.isfile(old_file.path):
        os.remove(old_file.path)


class CommunicationLogEntry(models.Model):
    """
    model to log the communication between the server and the PSUs
    """

    class Level(models.IntegerChoices):
        # used to sort entries and to set a lease time in command cleanlog
        # >= 100 long
        # >= 10 middle
        # otherwise short

        # errors
        MAJOR_ERROR = 200
        ERROR = 20
        MINOR_ERROR = 2

        # successful requests
        MAJOR_INFO = 100
        INFO = 10
        MINOR_INFO = 1

    # field to classify the log level
    level = models.IntegerField(_('classification'), choices=Level.choices)

    # field for storing the concerning PSU
    psu = models.ForeignKey(PSU, models.SET_NULL, verbose_name=_('Plant Supply Unit'), null=True)
    # field to keep the identity key even if the psu is deleted
    psu_identity_key = models.CharField(_('psu identity key'), max_length=128)

    # timestamp of the action
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)

    # field for storing the URL
    request_uri = models.CharField(_('request uri'), max_length=200)

    # field for storing a string reprensentation of the request
    request = models.TextField(_('request'))

    # field for storing the response given by the server
    response = models.TextField(_('repsonse'))

    def __str__(self):
        return 'L{} {} {} - {} ? {}'.format(self.level, self.psu_identity_key,
                                            self.timestamp.strftime('%d.%m.%Y %H:%M:%S'),
                                            self.request_uri, self.request)

    class Meta:
        verbose_name = _('Log Entry')
        verbose_name_plural = _('Log Entries')
        ordering = ['-timestamp', '-level']
