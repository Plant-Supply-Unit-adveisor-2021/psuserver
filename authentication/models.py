from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from authentication.managers import UserManager

# Create your models here.
class User(AbstractUser):
    """
    User class to overwrite the default User class which cannot be modified
    """
    # from here https://docs.djangoproject.com/en/2.2/topics/auth/customizing/
    # https://testdriven.io/blog/django-custom-user-model/

    # the login name is the email
    username = None
    email = models.EmailField(_('e-mail address'), unique=True)

    # basic personal information
    first_name = models.CharField(_('first name'), max_length=255)
    last_name = models.CharField(_('last name'), max_length=255)

    # addtional fields
    darkmode = models.BooleanField(_('darkmode active'), default=False)


    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    # all of them are required
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    # Generic string value for User
    def __str__(self):
        return '{} {} - {}'.format(self.first_name, self.last_name, self.email)

    # additional functions
    def darkmode_active(self):
        return self.darkmode

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ["last_name", "first_name"]