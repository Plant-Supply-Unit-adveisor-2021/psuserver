from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PsufrontendConfig(AppConfig):
    name = 'psufrontend'
    verbose_name = _('PSU Frontend')
