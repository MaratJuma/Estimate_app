from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import ServiceCategoryForm
from ..models import ServiceCategory
from ..permissions import can_manage_admin_panel, deny_access
from ..selectors.admin_categories import (
    get_admin_category_list_queryset,
    get_service_category_with_usage,
)
from ..services.admin_categories import delete_service_category_if_empty


def admin_dashboard(request):
    if not can_manage_admin_panel(request.user):
        return deny_access(request, 'У вас нет прав на доступ к административному разделу.')

    return render(request, 'core/admin_dashboard.html')


def admin_category_list(request):
    if not can_manage_admin_panel(request.user):
        return deny_access(request, 'У вас нет прав на управление категориями.')

    categories = get_admin_category_list_queryset()

    return render(request, 'core/admin_category_list.html', {
        'categories': categories,
    })


def admin_category_create(request):
    if not can_manage_admin_panel(request.user):
        return deny_access(request, 'У вас нет прав на управление категориями.')

    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Категория "{category.name}" создана.')
            return redirect('admin_category_list')
    else:
        form = ServiceCategoryForm()

    return render(request, 'core/admin_category_form.html', {
        'form': form,
        'is_edit': False,
    })


def admin_category_update(request, category_id):
    if not can_manage_admin_panel(request.user):
        return deny_access(request, 'У вас нет прав на управление категориями.')

    category = get_object_or_404(ServiceCategory, id=category_id)

    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Категория "{category.name}" обновлена.')
            return redirect('admin_category_list')
    else:
        form = ServiceCategoryForm(instance=category)

    category_with_usage = get_service_category_with_usage(category.id)

    return render(request, 'core/admin_category_form.html', {
        'form': form,
        'is_edit': True,
        'category': category,
        'services_count': category_with_usage.services_count if category_with_usage else 0,
    })


def admin_category_delete(request, category_id):
    if not can_manage_admin_panel(request.user):
        return deny_access(request, 'У вас нет прав на управление категориями.')

    category = get_object_or_404(ServiceCategory, id=category_id)
    category_with_usage = get_service_category_with_usage(category.id)
    services_count = category_with_usage.services_count if category_with_usage else 0

    if services_count > 0:
        messages.error(
            request,
            f'Категорию "{category.name}" нельзя удалить, потому что в ней есть услуги ({services_count}).'
        )
        return redirect('admin_category_list')

    if request.method == 'POST':
        try:
            category_name = category.name
            delete_service_category_if_empty(category)
            messages.success(request, f'Категория "{category_name}" удалена.')
            return redirect('admin_category_list')
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect('admin_category_list')

    return render(request, 'core/admin_category_confirm_delete.html', {
        'category': category,
        'services_count': services_count,
    })