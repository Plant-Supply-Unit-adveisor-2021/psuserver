from django import forms
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError

from psucontrol.models import PendingPSU, PSU
import psufrontend.views


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


class ChangeUserPermissionsForm(forms.Form):
    """
    form for selecting a PSU and changing permissions for active users or add new users with permissions
    """
    #select_psu = forms.ChoiceField(label=_('Select psu: '), label_suffix=_(''), help_text=_('For which PSU do you want to change the user permissions?'))

    active_users = forms.ChoiceField(label=_('Active users: '), label_suffix=_(''),
                                     help_text=_('select permitted user to remove permissions'))

    select_user = forms.CharField(label=_('Select user'), max_length=100, min_length=1,
                                  help_text=_('Add a user that you want to give permissions to'))

    # stellt die PSUs, auf die der user Zugriff hat, in einem ChoiceField zur Auswahl
    def __init__(self, psus, users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.psus = psus
        #self.fields['select_psu'].choices = self.psus_choices()
        self.users = users
        self.fields['active_users'].choices = self.users_choices()

    """def psus_choices(self):
        strings = []
        for p in self.psus:
            strings.append((str(p), p))
        return strings"""

    # stellt die user, die auf die ausgewählte PSU Zugriff haben, in einem MultipleChoiceField zur Auswahl
    def users_choices(self):
        strings = []
        for u in self.users:
            strings.append((str(u), u))
        return strings
