from django.core.validators import URLValidator
from django.db import models

from apps.common.constants import MAX_PROJECT_NAME_LENGTH, MAX_STATUS_LENGTH


class Project(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Открыт'
        CLOSED = 'closed', 'Закрыт'

    name = models.CharField(
        max_length=MAX_PROJECT_NAME_LENGTH,
        verbose_name='Название проекта'
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='Описание'
    )
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    github_url = models.URLField(
        blank=True,
        default='',
        validators=[URLValidator()],
        verbose_name='GitHub'
    )
    status = models.CharField(
        max_length=MAX_STATUS_LENGTH,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name='Статус'
    )
    participants = models.ManyToManyField(
        'users.User',
        related_name='participated_projects',
        blank=True,
        verbose_name='Участники'
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
