from django.contrib import messages
from django.shortcuts import redirect

def deny_access(request, message='У вас нет прав для выполнения этого действия.'):
    messages.error(request, message)
    return redirect('estimate_list')

def is_admin(user):
    return user.is_authenticated and user.is_superuser


def is_production_manager(user):
    return user.is_authenticated and user.groups.filter(name='production_manager').exists()


def is_sales_manager(user):
    return user.is_authenticated and user.groups.filter(name='sales_manager').exists()


def can_view_estimates(user):
    return is_admin(user) or is_production_manager(user) or is_sales_manager(user)


def can_edit_estimates(user):
    return is_admin(user) or is_sales_manager(user)


def can_approve_estimates(user):
    return is_admin(user) or is_production_manager(user)


def can_manage_services(user):
    return is_admin(user) or is_production_manager(user)


def can_manage_contractors(user):
    return is_admin(user) or is_production_manager(user)