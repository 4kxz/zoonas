from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext as _

from .models import User


class RegisterForm(forms.Form):
    username = forms.RegexField(
        label=_("Username"),
        max_length=20,
        regex=r'^[A-Za-z0-9-]{2,20}$',
        )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        max_length=256,
        )
    password_check = forms.CharField(
        label=_("Repeat password"),
        widget=forms.PasswordInput,
        max_length=256,
        )
    captcha = ReCaptchaField(
        attrs={'theme' : 'clean'},
        )

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _("Submit")))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_("Username already used."))
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 4:
            raise forms.ValidationError(_("Password too lame, try a new one."))
        if len(password) > 256:
            raise forms.ValidationError(_("256 characters should be enough."))
        return password

    def clean_password_check(self):
        # TODO: check _check
        try:
            password = self.cleaned_data['password']
        except KeyError:
            pass
        else:
            password_check = self.cleaned_data['password_check']
            if password != password_check:
                raise forms.ValidationError(_("Passwords must match."))
            return password_check


class EraseForm(forms.Form):
    username = forms.CharField(
        label=_("Username"),
        )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        max_length=256,
        )

    def __init__(self, *args, **kwargs):
        super(EraseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _("Erase")))


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _("Login")))


class PasswordForm(forms.Form):
    password = forms.CharField(
        label=_("Current password"),
        widget=forms.PasswordInput,
        max_length=256,
        )
    new_password_1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        max_length=256,
        )
    new_password_2 = forms.CharField(
        label=_("Repeat new password"),
        widget=forms.PasswordInput,
        max_length=256,
        )

    def __init__(self, *args, **kwargs):
        super(PasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _("Update")))

    # Check if passwords match
    def clean_new_password_2(self):
        try:
            password_1 = self.cleaned_data['new_password_1']
            password_2 = self.cleaned_data['new_password_2']
        except KeyError:
            raise forms.ValidationError(_("Fill all passwords."))
        if password_1 != password_2:
            raise forms.ValidationError(_("Passwords must match."))
        if len(password_1) < 4:
            raise forms.ValidationError(_("Password too lame, try a new one."))
        if len(password_1) > 256:
            raise forms.ValidationError(_("256 characters should be enough."))
        return password_2
