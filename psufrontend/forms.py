from django import forms
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import ValidationError

from psucontrol.models import PendingPSU

class RegisterPSUForm(forms.Form):
    """
    form for registering a PSU and converting a PendingPSU into a PSU
    """
    pairing_key = forms.CharField(label=_('Pairing key'), max_length=6, min_length=6,
                                  help_text=_('This key should be displayed on your PSU.'))
    name = forms.CharField(label=_('PSU name'), max_length=128, min_length=6,
                            help_text=_('Choose a name to identify this particular PSU.'))

    def clean(self):
        if PendingPSU.objects.filter(pairing_key=self.cleaned_data['pairing_key']).count() == 0:
            raise ValidationError(_("Sadly we could not match the given pairing key. Please check wether "
                                    "the key is correct and wether your PSU has a internet connection."))
        return self.cleaned_data