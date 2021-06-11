from django import forms
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError

from psucontrol.models import PendingPSU, to_psu, PSU, WateringParams


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
            raise ValidationError(_("Sadly we could not match the given pairing key. Please check whether "
                                    "the key is correct and whether your PSU has a internet connection."))
        return self.cleaned_data


class AddWateringTaskForm(forms.Form):
    """
    form to add a new WateringTask
    """
    psu = forms.TypedChoiceField(label=_('Plant Supply Unit'), choices=[], help_text=_('The PSU you want to water manually.'), coerce=to_psu)
    amount = forms.IntegerField(label=_('Amount of water'), help_text=_('The amount of water in milliliters you want to give to your plant.'))

    def __init__(self, psus, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # initialize choice field wit h PSUs
        choices = []
        for p in psus:
            choices.append((p,p.pretty_name()))
        self.fields['psu'].choices = choices

    def clean(self):
        if self.cleaned_data['amount'] <= 0:
            raise ValidationError(_('Please enter an amount of water that is bigger than zero.'))
        return self.cleaned_data

class WateringControlForm(forms.Form):
    """
    form to change watering parameters and choose if you want to water manually
    """
    param = forms.TypedChoiceField(label=_('Watering Paramter'), choices=[], help_text=_('Choose your watering parameter.'), coerce=to_psu)
    unauthorized_watering = forms.BooleanField(label='Water PSU manually', required=False, help_text=_('Select if you want to water you PSU yourself'))

    def __init__(self, wateringparameter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # initialize choice field with parameters
        choices = []
        for w in wateringparameter:
            choices.append(w)
        self.fields['param'].choices = choices

