
from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from captcha.fields import CaptchaField


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'captcha']


class EditProfileForm(UserChangeForm):

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name'
        )