import re
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.utils import timezone


def validate_phone(value):
    """Валидация телефонного номера"""
    if not value:
        return value

    # временный номер для новых пользователей
    if value == '+70000000000':
        return value

    if not re.match(r'^(\+7|8)\d{10}$', value):
        raise ValidationError(
            'Номер телефона должен быть в формате '
            '8XXXXXXXXXX или +7XXXXXXXXXX'
        )

    normalized = value
    if normalized.startswith('8'):
        normalized = '+7' + normalized[1:]

    return normalized


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, phone,
                    password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            surname=surname,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, phone,
                         password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(
            email, name, surname, phone, password, **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    name = models.CharField(max_length=124, verbose_name='Имя')
    surname = models.CharField(max_length=124, verbose_name='Фамилия')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    phone = models.CharField(
        max_length=12,
        validators=[validate_phone],
        verbose_name='Телефон',
        blank=True,
        null=True,
        default='+70000000000'
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        verbose_name='GitHub'
    )
    about = models.TextField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name='О себе'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата регистрации'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата создания'
    )

    favorites = models.ManyToManyField(
        'projects.Project',
        related_name='interested_users',
        blank=True,
        verbose_name='Избранное'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'phone']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Нормализуем телефон
        if self.phone:
            if self.phone.startswith('8'):
                self.phone = '+7' + self.phone[1:]

        super().save(*args, **kwargs)

    def get_full_name(self):
        return f'{self.name} {self.surname}'

    def __str__(self):
        return self.get_full_name()
