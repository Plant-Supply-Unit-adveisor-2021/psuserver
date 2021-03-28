from django import forms

from django.core.exceptions import ValidationError

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password, password_validators_help_text_html

from django.utils.translation import ugettext_lazy as _

from authentication.models import User

class LoginForm(forms.Form):
    """
    Form to login
    """

    email = forms.EmailField(required=True, label=_("E-Mail"))
    password = forms.CharField(widget=forms.PasswordInput, required=True, label=_("Password"))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = authenticate(email=email, password=password)
        if not user:
            raise forms.ValidationError(_('Mail and password do not match or your account is not activate yet.'))
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data


class EditProfileForm(forms.Form):
    """
    form for changing user information without the password
    """
    email = forms.EmailField(required=True, label=_("E-Mail"))
    first_name = forms.CharField(required=True, label=_("First Name"))
    last_name = forms.CharField(required=True, label=_("Last Name"))
    darkmode = forms.BooleanField(required=False, label=_("Darkmode"))
    
    def __init__(self, user, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = user.email
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
        self.fields['darkmode'].initial = user.darkmode

class ChangePasswordForm(forms.Form):
    """
    form for changing the users password
    """
    old_passwd = forms.CharField(required=False, label=_("Current Password"), widget=forms.PasswordInput, help_text=_("Leave clear to keep your current password."))
    new_passwd_1 = forms.CharField(required=False, label=_("New Password"), widget=forms.PasswordInput, help_text=password_validators_help_text_html())
    new_passwd_2 = forms.CharField(required=False, label=_("Confirm New Password"), widget=forms.PasswordInput)
    email = forms.CharField(required=True, widget=forms.HiddenInput)

    def __init__(self, user, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = user.email

    def clean(self):
        # Check wether user wants to change the password
        # Check wether new passwords do match
        if self.cleaned_data['old_passwd'] == '':
            return self.cleaned_data
        if self.cleaned_data['new_passwd_1'] != self.cleaned_data['new_passwd_2']:
            raise forms.ValidationError(_("The two given passwords do not match."))
        # run password validatiors sepcified in setting.py
        validate_password(self.cleaned_data['new_passwd_1'])
        if authenticate(email=self.cleaned_data['email'], password=self.cleaned_data['old_passwd']) is None:
            raise forms.ValidationError(_("Please enter your current password correctly to change your password."))
        return self.cleaned_data
        

class RegisterForm(forms.Form):
    """
    form for signing up
    """
    email = forms.EmailField(required=True, label=_("E-Mail"))
    first_name = forms.CharField(required=True, label=_("First Name"))
    last_name = forms.CharField(required=True, label=_("Last Name"))
    passwd_1 = forms.CharField(required=False, label=_("Password"), widget=forms.PasswordInput, help_text=password_validators_help_text_html())
    passwd_2 = forms.CharField(required=False, label=_("Confirm Password"), widget=forms.PasswordInput)

    def clean(self):
        # Check wether passwords do match
        if self.cleaned_data['passwd_1'] != self.cleaned_data['passwd_2']:
            raise forms.ValidationError(_("The two given passwords do not match."))
        # Check wether email is unique
        if User.objects.filter(email=self.cleaned_data['email']).count() != 0:
            raise forms.ValidationError(_("The given e-mail address is already used by another user."))
        # run password validatiors sepcified in setting.py
        validate_password(self.cleaned_data['passwd_1'])
        return self.cleaned_data
