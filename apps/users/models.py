from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.utils import timezone

from apps.common.constants import (DEFAULT_PHONE, MAX_ABOUT_LENGTH,
                                   MAX_NAME_LENGTH, MAX_PHONE_LENGTH)
from apps.common.validators import validate_phone_number


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        phone = validate_phone_number(phone)
        if phone and User.objects.filter(phone=phone).exists():
            raise ValidationError('Пользователь с таким номером телефона уже существует')
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

    def create_superuser(self, email, name, surname, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, name, surname, phone, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    name = models.CharField(max_length=MAX_NAME_LENGTH, verbose_name='Имя')
    surname = models.CharField(max_length=MAX_NAME_LENGTH, verbose_name='Фамилия')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        default='',
        verbose_name='Аватар'
    )
    phone = models.CharField(
        max_length=MAX_PHONE_LENGTH,
        blank=True,
        default=DEFAULT_PHONE,
        verbose_name='Телефон'
    )
    github_url = models.URLField(
        blank=True,
        default='',
        validators=[URLValidator()],
        verbose_name='GitHub'
    )
    about = models.TextField(
        max_length=MAX_ABOUT_LENGTH,
        blank=True,
        default='',
        verbose_name='О себе'
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
        if self.phone and self.phone.startswith('8'):
            self.phone = '+7' + self.phone[1:]
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f'{self.name} {self.surname}'

    def __str__(self):
        return self.get_full_name()
