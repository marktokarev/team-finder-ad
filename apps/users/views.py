from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .models import User
from .forms import UserRegistrationForm, UserLoginForm, UserProfileEditForm


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Регистрация прошла успешно! Теперь вы можете войти.'
            )
            return redirect('users:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(
                    request,
                    f'Добро пожаловать, {user.get_full_name()}!'
                )
                return redirect('projects:project_list')
            else:
                form.add_error(None, 'Неверный email или пароль')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('projects:project_list')


def user_detail_view(request, user_id):
    user_profile = get_object_or_404(User, id=user_id)
    projects = user_profile.owned_projects.filter(status='open')
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'user': user_profile,
        'projects': page_obj,
    }
    return render(request, 'users/user-details.html', context)


@login_required
def edit_profile_view(request, user_id):
    if request.user.id != user_id and not request.user.is_staff:
        messages.error(request, 'У вас нет прав для редактирования этого '
                                'профиля')
        return redirect('users:user_detail', user_id=user_id)

    user_profile = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserProfileEditForm(
            request.POST,
            request.FILES,
            instance=user_profile
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('users:user_detail', user_id=user_id)
    else:
        form = UserProfileEditForm(instance=user_profile)

    return render(
        request,
        'users/edit_profile.html',
        {'form': form, 'profile_user': user_profile}
    )


@login_required
def change_password_view(request, user_id):
    if request.user.id != user_id:
        messages.error(
            request,
            'У вас нет прав для изменения пароля этого пользователя'
        )
        return redirect('users:user_detail', user_id=user_id)

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен')
            return redirect('users:user_detail', user_id=user_id)
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'users/change_password.html', {'form': form})


def participants_list_view(request):

    participants = User.objects.filter(is_active=True).order_by('-created_at')
    filter_type = request.GET.get('filter')
    active_filter = ''

    if request.user.is_authenticated and filter_type:
        active_filter = filter_type

        if filter_type == 'owners-of-favorite-projects':
            favorite_projects = request.user.favorites.all()
            participants = participants.filter(
                owned_projects__in=favorite_projects
            ).distinct()

        elif filter_type == 'owners-of-participating-projects':
            my_projects = request.user.participated_projects.all()
            participants = participants.filter(
                owned_projects__in=my_projects
            ).distinct()

        elif filter_type == 'interested-in-my-projects':
            # Пользователи, которым нравятся мои проекты
            my_projects = request.user.owned_projects.all()
            participants = participants.filter(
                favorites__in=my_projects
            ).distinct()

        elif filter_type == 'participants-of-my-projects':
            # Участники моих проектов
            my_projects = request.user.owned_projects.all()
            participants = participants.filter(
                participated_projects__in=my_projects
            ).distinct()

    paginator = Paginator(participants, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'participants': page_obj,
        'active_filter': active_filter,
    }
    return render(request, 'users/participants.html', context)
