from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6,
                                                 'class': 'form-control'}),
            'status': forms.Select(
                attrs={'class': 'form-control'},
                choices=Project.STATUS_CHOICES
            ),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Название проекта',
            'description': 'Описание проекта',
            'github_url': 'Ссылка на GitHub',
            'status': 'Статус проекта',
        }

    def clean_github_url(self):
        """Валидация ссылки на GitHub"""
        url = self.cleaned_data.get('github_url')
        if url and url.strip():
            if 'github.com' not in url:
                raise forms.ValidationError('Ссылка должна вести на GitHub')
        return url

    def clean_name(self):
        """Валидация названия проекта"""
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 3:
                raise forms.ValidationError(
                    'Название проекта должно содержать минимум 3 символа'
                )
            if len(name) > 200:
                raise forms.ValidationError(
                    'Название проекта не должно превышать 200 символов'
                )
        return name
