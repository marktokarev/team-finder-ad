from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from apps.common.pagination import paginate_queryset
from apps.projects.constants import PROJECT_STATUS_OPEN

from .constants import (FILTER_FAVORITE_AUTHORS,
                        FILTER_INTERESTED_IN_MY_PROJECTS,
                        FILTER_PARTICIPANTS_OF_MY_PROJECTS,
                        FILTER_PARTICIPATING_PROJECTS)
from .forms import UserLoginForm, UserProfileEditForm, UserRegistrationForm
from .models import User


def register_view(request):
    if request.method != 'POST':
        form = UserRegistrationForm()
        return render(request, 'users/register.html', {'form': form})
    form = UserRegistrationForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'users/register.html', {'form': form})
    form.save()
    messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти.')
    return redirect('users:login')


def login_view(request):
    if request.method != 'POST':
        form = UserLoginForm()
        return render(request, 'users/login.html', {'form': form})
    form = UserLoginForm(data=request.POST or None)
    if not form.is_valid():
        return render(request, 'users/login.html', {'form': form})
    email = form.cleaned_data.get('email')
    password = form.cleaned_data.get('password')
    user = authenticate(request, username=email, password=password)
    if user is None:
        return render(request, 'users/login.html', {'form': form})
    login(request, user)
    messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
    return redirect('projects:project_list')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('projects:project_list')


def user_detail_view(request, user_id):
    user_profile = get_object_or_404(User, id=user_id)
    projects = (
        user_profile.owned_projects
        .filter(status=PROJECT_STATUS_OPEN)
        .select_related('owner')
        .prefetch_related('participants')
        .order_by('-created_at')
    )
    page_obj = paginate_queryset(projects, request.GET.get('page'))
    context = {
        'user': user_profile,
        'projects': page_obj,
    }
    return render(request, 'users/user-details.html', context)


@login_required
def edit_profile_view(request, user_id):
    if request.user.id != user_id and not request.user.is_staff:
        messages.error(request, 'У вас нет прав для редактирования этого профиля')
        return redirect('users:user_detail', user_id=user_id)
    user_profile = get_object_or_404(User, id=user_id)
    if request.method != 'POST':
        form = UserProfileEditForm(instance=user_profile)
        return render(
            request,
            'users/edit_profile.html',
            {'form': form, 'profile_user': user_profile}
        )
    form = UserProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=user_profile
    )
    if not form.is_valid():
        return render(
            request,
            'users/edit_profile.html',
            {'form': form, 'profile_user': user_profile}
        )
    form.save()
    messages.success(request, 'Профиль успешно обновлен')
    return redirect('users:user_detail', user_id=user_id)


@login_required
def change_password_view(request, user_id):
    if request.user.id != user_id:
        messages.error(
            request,
            'У вас нет прав для изменения пароля этого пользователя'
        )
        return redirect('users:user_detail', user_id=user_id)
    if request.method != 'POST':
        form = PasswordChangeForm(request.user)
        return render(request, 'users/change_password.html', {'form': form})
    form = PasswordChangeForm(request.user, request.POST or None)
    if not form.is_valid():
        return render(request, 'users/change_password.html', {'form': form})
    user = form.save()
    update_session_auth_hash(request, user)
    messages.success(request, 'Пароль успешно изменен')
    return redirect('users:user_detail', user_id=user_id)


def participants_list_view(request):
    participants = User.objects.filter(is_active=True).order_by('-created_at')
    filter_type = request.GET.get('filter')
    active_filter = ''
    if request.user.is_authenticated and filter_type:
        active_filter = filter_type
        if filter_type == FILTER_FAVORITE_AUTHORS:
            favorite_projects = request.user.favorites.all()
            participants = participants.filter(
                owned_projects__in=favorite_projects
            ).distinct()
        elif filter_type == FILTER_PARTICIPATING_PROJECTS:
            my_projects = request.user.participated_projects.all()
            participants = participants.filter(
                owned_projects__in=my_projects
            ).distinct()
        elif filter_type == FILTER_INTERESTED_IN_MY_PROJECTS:
            my_projects = request.user.owned_projects.all()
            participants = participants.filter(
                favorites__in=my_projects
            ).distinct()
        elif filter_type == FILTER_PARTICIPANTS_OF_MY_PROJECTS:
            my_projects = request.user.owned_projects.all()
            participants = participants.filter(
                participated_projects__in=my_projects
            ).distinct()
    page_obj = paginate_queryset(participants, request.GET.get('page'))
    context = {
        'participants': page_obj,
        'active_filter': active_filter,
    }
    return render(request, 'users/participants.html', context)
