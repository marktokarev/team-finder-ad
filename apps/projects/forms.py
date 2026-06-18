from django import forms

from apps.common.validators import validate_github_url, validate_project_name

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'status': forms.Select(
                attrs={'class': 'form-control'},
                choices=Project.Status.choices
            ),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        return validate_github_url(url)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        return validate_project_name(name)
