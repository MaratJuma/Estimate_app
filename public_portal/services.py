from django.contrib.auth import get_user_model
from django.db import transaction
from django_tenants.utils import tenant_context

from customers.models import Client, Domain
from core.models import CompanyProfile

User = get_user_model()


def build_tenant_domain(subdomain, base_host):
    return f'{subdomain}.{base_host}'


@transaction.atomic
def provision_tenant_with_admin(
    *,
    company_name,
    subdomain,
    admin_username,
    admin_email,
    password,
    base_domain,
    phone='',
    company_email='',
    website='',
    address='',
):
    tenant = Client.objects.create(
        schema_name=subdomain,
        name=company_name,
    )

    full_domain = build_tenant_domain(subdomain, base_domain)

    Domain.objects.create(
        domain=full_domain,
        tenant=tenant,
        is_primary=True,
    )

    with tenant_context(tenant):
        User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=password,
        )

        CompanyProfile.objects.get_or_create(
            id=1,
            defaults={
                'name': company_name,
                'phone': phone,
                'email': company_email,
                'site': website,
                'address': address,
                'manager_title': 'Администратор',
                'manager_name': '',
            }
        )

    return {
        'tenant': tenant,
        'domain': full_domain,
    }