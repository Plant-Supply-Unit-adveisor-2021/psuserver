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


class AddUserPermissionsForm(forms.Form):
    """
    form for adding a user and giving him the permission on a selected psu
    """

    user_mail = forms.EmailField(label=_('E-Mail of the User'), max_length=100, min_length=1,
                                 help_text=_('This should be the email address of the user you want to give permissions to.'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        try:
            self.cleaned_data['user'] = User.objects.get(email=self.cleaned_data['user_mail'])
        except KeyError:
            # mail validation failed
            pass
        except User.DoesNotExist:
            # user does not exist
            raise ValidationError(_('We could not find a user with this mail address in our system. Please make shure there is an account linked to this mail address.'))

        return self.cleaned_data


class RevokeUserPermissionsForm(forms.Form):
    """
    form for selecting an active user and revoking his/her permissions on a selected psu
    """

    revoke_user = forms.ChoiceField(label=_('User to revoke Permissions'), label_suffix=_(''),
                                    help_text=_('Select a user you want to take away the permissions for this PSU.'))

    def __init__(self, users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        for u in users:
            choices.append((u.email, u))
        self.fields['revoke_user'].choices = choices

    def clean(self):
        try:
            self.cleaned_data['user'] = User.objects.get(email=self.cleaned_data['revoke_user'])
        except KeyError:
            # weird error should already be catched in advance
            pass
        except User.DoesNotExist:
            # user does not exist
            raise ValidationError(_('We could not find a user the user you wanted to revoke permissions of. Please try again.'))

        return self.cleaned_data


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
