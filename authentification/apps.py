from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AuthentificationConfig(AppConfig):
    name = 'authentification'
    verbose_name = _('Authentification')
