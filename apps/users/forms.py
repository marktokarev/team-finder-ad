import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import User


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль'
    )

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'email': 'Email',
        }
        widgets = {
            'name': forms.TextInput(attrs={'required': True}),
            'surname': forms.TextInput(attrs={'required': True}),
            'email': forms.EmailInput(attrs={'required': True}),
            'password': forms.PasswordInput(attrs={'required': True}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        # Устанавливаем временный телефон
        user.phone = '+70000000000'
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = self.fields.pop('username')
        self.fields['email'].label = 'Email'
        self.fields['email'].widget = forms.EmailInput(attrs={
            'class': 'form-control'
            })
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control'
            })


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        widgets = {
            'about': forms.Textarea(
                attrs={'rows': 4, 'class': 'form-control'}
            ),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '+71234567890'}
                ),
            'github_url': forms.URLInput(
                attrs={'class': 'form-control',
                       'placeholder': 'https://github.com/username'}
                ),
            'avatar': forms.FileInput(
                attrs={'class': 'form-control'}
                ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone or phone.strip() == '':
            return None
        phone = phone.strip()
        phone = phone.replace(' ', '')
        phone = phone.replace('-', '')
        phone = phone.replace('(', '')
        phone = phone.replace(')', '')
        if phone.startswith('+'):
            phone = '+' + ''.join(filter(str.isdigit, phone[1:]))
        else:
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) == 10:
                phone = '+7' + phone
            elif len(phone) == 11 and phone.startswith('8'):
                phone = '+7' + phone[1:]
            elif len(phone) == 11 and phone.startswith('7'):
                phone = '+' + phone

        if not re.match(r'^\+7\d{10}$', phone):
            raise ValidationError(
                'Введите корректный номер телефона. '
                'Примеры: +79123456789, 89123456789, 9123456789'
            )

        if User.objects.filter(phone=phone).exclude(
                id=self.instance.id).exists():
            raise ValidationError('Этот номер телефона уже используется')

        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url and url.strip():
            if 'github.com' not in url:
                raise ValidationError('Ссылка должна вести на GitHub')
        return url
