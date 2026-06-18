from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'owner__email')
    filter_horizontal = ('participants',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'owner', 'status')
        }),
        ('Links', {
            'fields': ('github_url',)
        }),
        ('Participants', {
            'fields': ('participants',)
        }),
        ('Dates', {
            'fields': ('created_at',)
        }),
    )
