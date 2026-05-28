from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from ..forms import AdminUserCreateForm, AdminUserUpdateForm
from ..permissions import can_manage_admin_panel, deny_access
from ..selectors.admin_users import get_admin_user_list_queryset, get_user_with_groups
from ..services.admin_users import (
    create_user_with_role,
    update_user_with_role,
    delete_user_with_guards,
    get_user_role,
)

User = get_user_model()

@login_required
def admin_user_list(request):
    if not can_manage_admin_panel(request.user):
        return deny_access(request, 'У вас нет прав на управление пользователями.')

    users = get_admin_user_list_queryset()

    user_rows = []
    for user in users:
        display_name = f'{user.first_name} {user.last_name}'.strip()
        user_rows.append({
            'obj': user,
            'display_name': display_name or '—',
            'role': get_user_role(user),
            'can_delete': user.id != request.user.id,
        })

    return render(request, 'core/admin_user_list.html', {
        'user_rows': user_rows,
    })

@login_required
def admin_user_create(request):
    if not can_manage_admin_panel(request.user):
        return deny_access(request, 'У вас нет прав на управление пользователями.')

    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            user = create_user_with_role(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', ''),
                is_active=form.cleaned_data.get('is_active', True),
                role=form.cleaned_data['role'],
            )
            messages.success(request, f'Пользователь "{user.username}" создан.')
            return redirect('admin_user_list')
    else:
        form = AdminUserCreateForm()

    return render(request, 'core/admin_user_form.html', {
        'form': form,
        'is_edit': False,
    })

@login_required
def admin_user_update(request, user_id):
    if not can_manage_admin_panel(request.user):
        return deny_access(request, 'У вас нет прав на управление пользователями.')

    target_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=target_user)
        if form.is_valid():
            update_user_with_role(
                target_user,
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', ''),
                is_active=form.cleaned_data.get('is_active', True),
                role=form.cleaned_data['role'],
                new_password=form.cleaned_data.get('new_password1', ''),
            )
            messages.success(request, f'Пользователь "{target_user.username}" обновлён.')
            return redirect('admin_user_list')
    else:
        form = AdminUserUpdateForm(instance=target_user)

    current_role = get_user_role(target_user)

    return render(request, 'core/admin_user_form.html', {
        'form': form,
        'is_edit': True,
        'target_user': target_user,
        'current_role': current_role,
        'can_delete': target_user.id != request.user.id,
    })

@login_required
def admin_user_delete(request, user_id):
    if not can_manage_admin_panel(request.user):
        return deny_access(request, 'У вас нет прав на управление пользователями.')

    target_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        try:
            username = target_user.username
            delete_user_with_guards(target_user, request.user)
            messages.success(request, f'Пользователь "{username}" удалён.')
            return redirect('admin_user_list')
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect('admin_user_list')

    current_role = get_user_role(target_user)

    return render(request, 'core/admin_user_confirm_delete.html', {
        'target_user': target_user,
        'current_role': current_role,
        'is_self_delete': target_user.id == request.user.id,
    })