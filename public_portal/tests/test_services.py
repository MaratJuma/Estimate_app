from django.contrib.auth import get_user_model
from django.test import TestCase
from django_tenants.utils import tenant_context

from core.models import CompanyProfile
from customers.models import Client, Domain
from public_portal.services import provision_tenant_with_admin
from django_tenants.utils import schema_context

User = get_user_model()


class ProvisionTenantWithAdminTests(TestCase):
    def test_provision_creates_tenant_domain_admin_and_company_profile(self):
        with schema_context('public'):
            result = provision_tenant_with_admin(
                company_name='Demo Company',
                subdomain='demo2',
                admin_username='admin',
                admin_email='admin@demo.com',
                password='admin12345',
                base_domain='lvh.me',
                phone='+79990000000',
                company_email='info@demo.com',
                website='https://demo2.com',
                address='Moscow',
            )

        tenant = Client.objects.get(schema_name='demo2')
        domain = Domain.objects.get(domain='demo2.lvh.me')

        self.assertEqual(result['tenant'].id, tenant.id)
        self.assertEqual(result['domain'], 'demo2.lvh.me')
        self.assertEqual(domain.tenant, tenant)
        self.assertTrue(domain.is_primary)

        with tenant_context(tenant):
            user = User.objects.get(username='admin')
            self.assertEqual(user.email, 'admin@demo.com')
            self.assertTrue(user.is_superuser)
            self.assertTrue(user.is_staff)
            self.assertTrue(user.check_password('admin12345'))

            profile = CompanyProfile.objects.get(id=1)
            self.assertEqual(profile.name, 'Demo Company')
            self.assertEqual(profile.phone, '+79990000000')
            self.assertEqual(profile.email, 'info@demo.com')
            self.assertEqual(profile.site, 'https://demo2.com')
            self.assertEqual(profile.address, 'Moscow')