from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'name', 'surname', 'phone', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'name', 'surname')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {
            'fields': (
                'name',
                'surname',
                'avatar',
                'phone',
                'github_url',
                'about'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Favorites', {'fields': ('favorites',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'name',
                'surname',
                'phone',
                'password1',
                'password2'
            ),
        }),
    )
