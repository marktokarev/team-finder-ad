from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Project
from .forms import ProjectForm


def project_list_view(request):
    projects = Project.objects.filter(status='open').order_by('-created_at')
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'projects': page_obj,
    }
    return render(request, 'projects/project_list.html', context)


def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(
        request,
        'projects/project-details.html',
        {'project': project}
        )


@login_required
def create_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.created_at = timezone.now()
            project.save()
            project.participants.add(request.user)
            messages.success(request, 'Проект успешно создан!')
            return redirect('projects:project_detail', project_id=project.id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = ProjectForm()

    return render(
        request,
        'projects/create-project.html',
        {'form': form, 'is_edit': False}
    )


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user and not request.user.is_staff:
        messages.error(request, 'Вы не можете редактировать этот проект')
        return redirect('projects:project_detail', project_id=project_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Проект успешно обновлен!')
            return redirect('projects:project_detail', project_id=project_id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        'projects/create-project.html',
        {'form': form, 'is_edit': True, 'project': project}
    )


@login_required
@require_POST
def toggle_favorite_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project in request.user.favorites.all():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True

    return JsonResponse({'status': 'ok', 'favorited': favorited})


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.status != 'open':
        return JsonResponse({
            'status': 'error',
            'message': 'Проект закрыт для участия'
        }, status=400)

    if request.user in project.participants.all():
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return redirect('projects:project_detail', project_id=project.id)


@login_required
@require_POST
def complete_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse({
            'status': 'error',
            'message': 'У вас нет прав для завершения этого проекта'
        }, status=403)

    if project.status == 'open':
        project.status = 'closed'
        project.save()
        return JsonResponse({
            'status': 'ok',
            'project_status': 'closed'
        })

    return JsonResponse({
        'status': 'error',
        'message': 'Проект уже завершен'
    }, status=400)


@login_required
def favorites_list_view(request):
    projects = request.user.favorites.all().order_by('-created_at')

    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'projects/favorite_projects.html',
        {'projects': page_obj}
        )
