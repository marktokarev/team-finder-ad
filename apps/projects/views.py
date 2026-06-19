from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.common.constants import DEFAULT_PAGE
from apps.common.pagination import paginate_queryset

from .forms import ProjectForm
from .models import Project


def project_list_view(request):
    projects = (
        Project.objects
        .filter(status=Project.Status.OPEN)
        .select_related('owner')
        .prefetch_related('participants')
    )
    page_obj = paginate_queryset(
        projects,
        request.GET.get('page', DEFAULT_PAGE)
    )
    context = {
        'projects': page_obj,
    }
    return render(request, 'projects/project_list.html', context)


def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related('owner').prefetch_related('participants'),
        id=project_id
    )
    return render(request, 'projects/project-details.html', {'project': project})


@login_required
def create_project_view(request):
    form = (
        ProjectForm(request.POST or None)
        if request.method == 'POST'
        else ProjectForm()
    )
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        messages.success(request, 'Проект успешно создан!')
        return redirect('projects:project_detail', project_id=project.id)
    return render(
        request,
        'projects/create-project.html',
        {'form': form, 'is_edit': False}
    )


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user and not request.user.is_staff:
        messages.error(
            request,
            'У вас нет прав для редактирования этого проекта'
        )
        return redirect('projects:project_detail', project_id=project_id)
    form = (
        ProjectForm(request.POST or None, instance=project)
        if request.method == 'POST'
        else ProjectForm(instance=project)
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Проект успешно обновлен!')
        return redirect('projects:project_detail', project_id=project_id)
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
    if project.status != Project.Status.OPEN:
        return JsonResponse({
            'status': 'error',
            'message': 'Проект закрыт для участия'
        }, status=HTTPStatus.BAD_REQUEST)
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        participated = False
    else:
        project.participants.add(request.user)
        participated = True
    return JsonResponse({'status': 'ok', 'participated': participated})


@login_required
@require_POST
def complete_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse({
            'status': 'error',
            'message': 'У вас нет прав для завершения этого проекта'
        }, status=HTTPStatus.FORBIDDEN)

    if project.status != Project.Status.OPEN:
        return JsonResponse({
            'status': 'error',
            'message': 'Проект уже завершен'
        }, status=HTTPStatus.BAD_REQUEST)
    project.status = Project.Status.CLOSED
    project.save()
    return JsonResponse({
        'status': 'ok',
        'project_status': project.status
    })


@login_required
def favorites_list_view(request):
    projects = (
        request.user.favorites
        .select_related('owner')
        .prefetch_related('participants')
    )
    page_obj = paginate_queryset(
        projects,
        request.GET.get('page', DEFAULT_PAGE)
    )
    return render(
        request,
        'projects/favorite_projects.html',
        {'projects': page_obj}
    )
