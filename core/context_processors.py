from .models import CompanyProfile
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
    user = getattr(request, 'user', None)

    if user is None:
        return {
            'is_admin_user': False,
            'is_production_manager_user': False,
            'is_sales_manager_user': False,
            'can_view_estimates_ui': False,
            'can_edit_estimates_ui': False,
            'can_approve_estimates_ui': False,
            'can_manage_services_ui': False,
            'can_manage_contractors_ui': False,
            'role_name': '',
        }

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


def company_branding(request):
    default_platform_name = 'SistemaSmet'
    default_company_name = 'Компания'

    try:
        profile = CompanyProfile.objects.order_by('id').first()
    except Exception:
        profile = None

    company_name = profile.name if profile and profile.name else default_company_name
    company_tagline = profile.tagline if profile and profile.tagline else ''
    company_logo_url = profile.logo.url if profile and profile.logo else None

    return {
        'company_profile': profile,
        'company_name': company_name,
        'company_tagline': company_tagline,
        'company_logo_url': company_logo_url,
        'platform_name': default_platform_name,
    }