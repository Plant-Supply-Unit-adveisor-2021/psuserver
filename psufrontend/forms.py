from django import forms
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError

from psucontrol.models import PendingPSU, to_psu, to_watering_params
from authentication.models import User


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

    actions = [("1", "Give permissions to a user"), ("2", "Revoke permissions from a user")]
    select_action = forms.ChoiceField(label=_('Select action: '), label_suffix=_(''), choices=actions)

    def clean(self):
        cleaned_data = self.cleaned_data.get('select_action')
        return cleaned_data


class AddUserPermissionsForm(forms.Form):
    """
    form for adding users and giving them permissions on a selected psu
    """

    select_user = forms.CharField(label=_('Select user'), max_length=100, min_length=1,
                                  help_text=_('Type in the email-adress of a user that you want to give permissions to'))

    def __init__(self, sel_psu, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sel_psu = sel_psu

    def clean(self):
        if User.objects.get(email=self.cleaned_data.get('select_user')):
            if User.objects.get(email=self.cleaned_data.get('select_user')) in self.sel_psu.permitted_users.all():
                raise ValidationError(_("This user already has permissions on this PSU."))
            else:
                cleaned_data = self.cleaned_data.get('select_user')
        else:
            raise ValidationError(_("This user does not exist."))

        return cleaned_data


class RevokeUserPermissionsForm(forms.Form):
    """
    form for selecting an active user and revoking his/her permissions on a selected psu
    """

    active_users = forms.ChoiceField(label=_('Active users: '), label_suffix=_(''),
                                     help_text=_('select permitted user to remove permissions'))

    # stellt die user, die auf die ausgewählte PSU Zugriff haben, in einem MultipleChoiceField zur Auswahl
    def __init__(self, users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = users
        self.fields['active_users'].choices = self.users_choices()

    def users_choices(self):
        strings = []
        for u in self.users:
            strings.append((u.email, u))
        return strings

    def clean(self):
        cleaned_data = self.cleaned_data.get('active_users')
        return cleaned_data


class AddWateringTaskForm(forms.Form):
    """
    form to add a new WateringTask
    """
    amount = forms.IntegerField(label=_('Amount of water'), help_text=_('The amount of water in milliliters you want to give to your plant.'))

    def clean(self):
        if self.cleaned_data['amount'] <= 0:
            raise ValidationError(_('Please enter an amount of water that is bigger than zero.'))
        return self.cleaned_data

class WateringControlForm(forms.Form):
    """
    form to change watering parameters and choose if you want to water manually
    """
    watering_params = forms.TypedChoiceField(label=_('Watering Paramter'), choices=[], help_text=_('Please choose the watering parameter according to your plant.'), coerce=to_watering_params)
    unauthorized_watering = forms.BooleanField(label=_('Automatic Watering'), required=False, help_text=_('Let your PSU water your plant through an algorithm automatically.'))

    def __init__(self, wateringparameters, psu, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unauthorized_watering'].initial = psu.unauthorized_watering
        # initialize choice field with parameters
        choices = []
        for w in wateringparameters:
            choices.append((w,w.name))
        self.fields['watering_params'].choices = choices
        if not psu.watering_params is None:
            self.fields['watering_params'].initial = psu.watering_params
