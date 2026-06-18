from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from apps.common.validators import (
    validate_github_url,
    validate_phone_number,
)

from .models import User


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = validate_phone_number(phone)
        if User.objects.filter(phone=phone).exists():
            raise ValidationError('Пользователь с таким номером телефона уже существует')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Пароли не совпадают')
        return cleaned_data


class UserLoginForm(AuthenticationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = self.fields.pop('username')
        self.fields['email'].label = 'Email'
        self.fields['email'].widget = forms.EmailInput(attrs={'class': 'form-control'})


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = validate_phone_number(phone)
        if User.objects.filter(phone=phone).exclude(id=self.instance.id).exists():
            raise ValidationError('Пользователь с таким номером телефона уже существует')
        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        return validate_github_url(url)
