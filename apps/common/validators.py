import re

from django.core.exceptions import ValidationError

from apps.common.constants import (DEFAULT_PHONE, GITHUB_URL_PATTERN,
                                   MAX_PROJECT_NAME_LENGTH,
                                   MIN_PROJECT_NAME_LENGTH)


def validate_github_url(url):
    if url and url.strip() and GITHUB_URL_PATTERN not in url:
        raise ValidationError('Ссылка должна вести на GitHub')
    return url


def validate_phone_number(phone, exclude_user_id=None):
    if not phone or phone.strip() == '':
        return DEFAULT_PHONE
    phone = (
        phone.replace(' ', '')
        .replace('-', '')
        .replace('(', '')
        .replace(')', '')
    )
    if phone.startswith('8'):
        phone = '+7' + phone[1:]
    elif not phone.startswith('+7'):
        phone = '+7' + phone
    if not re.match(r'^\+7\d{10}$', phone):
        raise ValidationError(
            'Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX'
        )
    return phone


def validate_project_name(name):
    if name:
        name = name.strip()
        if len(name) < MIN_PROJECT_NAME_LENGTH:
            raise ValidationError(
                f'Название проекта должно содержать минимум {MIN_PROJECT_NAME_LENGTH} символа'
            )
        if len(name) > MAX_PROJECT_NAME_LENGTH:
            raise ValidationError(
                f'Название проекта не должно превышать {MAX_PROJECT_NAME_LENGTH} символов'
            )
    return name
