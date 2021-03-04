from django import forms

from django.core.exceptions import ValidationError

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.password_validation import validate_password, password_validators_help_text_html
from django.contrib.auth import authenticate

from django.utils.translation import ugettext as _


class LoginForm(forms.Form):
    """
    Form to login
    """

    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = _("e-mail")
        self.fields['password'].label = _("password")

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise forms.ValidationError(_('Mail and password do not match or your account is not activate yet.'))
        return self.cleaned_data

    def login(self, request):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        return user