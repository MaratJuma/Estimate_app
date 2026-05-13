from .permissions import (
    is_admin,
    is_production_manager,
    is_sales_manager,
    can_view_estimates,
    can_edit_estimates,
    can_approve_estimates,
    can_manage_services,
    can_manage_contractors,
)


def user_permissions(request):
    user = request.user

    if is_admin(user):
        role_name = 'Администратор'
    elif is_production_manager(user):
        role_name = 'Отдел производства'
    elif is_sales_manager(user):
        role_name = 'Отдел продаж'
    else:
        role_name = ''

    return {
        'is_admin_user': is_admin(user),
        'is_production_manager_user': is_production_manager(user),
        'is_sales_manager_user': is_sales_manager(user),

        'can_view_estimates_ui': can_view_estimates(user),
        'can_edit_estimates_ui': can_edit_estimates(user),
        'can_approve_estimates_ui': can_approve_estimates(user),
        'can_manage_services_ui': can_manage_services(user),
        'can_manage_contractors_ui': can_manage_contractors(user),

        'role_name': role_name,
    }