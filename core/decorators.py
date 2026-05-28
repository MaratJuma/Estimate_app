from functools import wraps

from django.shortcuts import get_object_or_404

from .models import Estimate
from .permissions import (
    deny_access,
    can_manage_admin_panel,
    can_view_estimates,
    can_edit_estimates,
    can_approve_estimates,
    can_manage_services,
    can_edit_estimate,
    can_delete_estimate,
    can_duplicate_estimate,
)
from .selectors.estimates import get_estimate_detail_queryset


def user_passes_permission(permission_func, message):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not permission_func(request.user):
                return deny_access(request, message)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


admin_required = user_passes_permission(
    can_manage_admin_panel,
    'У вас нет прав на доступ к административному разделу.',
)

estimate_view_required = user_passes_permission(
    can_view_estimates,
    'У вас нет прав на просмотр смет.',
)

estimate_edit_role_required = user_passes_permission(
    can_edit_estimates,
    'У вас нет прав на редактирование смет.',
)

estimate_approve_required = user_passes_permission(
    can_approve_estimates,
    'У вас нет прав на утверждение смет.',
)

services_manage_required = user_passes_permission(
    can_manage_services,
    'У вас нет прав на управление услугами.',
)


def estimate_object_permission_required(permission_func, message):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            estimate_id = kwargs.get('estimate_id')
            if estimate_id is None:
                return deny_access(request, 'Не удалось определить смету для проверки прав.')

            estimate = get_object_or_404(
                get_estimate_detail_queryset(),
                id=estimate_id,
            )

            if not permission_func(request.user, estimate):
                return deny_access(request, message)

            kwargs['estimate'] = estimate
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


estimate_edit_required = estimate_object_permission_required(
    can_edit_estimate,
    'У вас нет прав на редактирование этой сметы.',
)

estimate_delete_required = estimate_object_permission_required(
    can_delete_estimate,
    'У вас нет прав на удаление этой сметы.',
)

estimate_duplicate_required = estimate_object_permission_required(
    can_duplicate_estimate,
    'У вас нет прав на дублирование смет.',
)