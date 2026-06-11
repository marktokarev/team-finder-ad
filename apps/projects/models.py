from django.core.validators import URLValidator
from django.db import models
from django.utils import timezone


class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открыт'),
        ('closed', 'Закрыт'),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name='Название проекта'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата создания'
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        verbose_name='GitHub'
    )
    status = models.CharField(
        max_length=6,
        choices=STATUS_CHOICES,
        default='open',
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
