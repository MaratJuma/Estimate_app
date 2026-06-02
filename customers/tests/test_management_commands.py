from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django_tenants.utils import tenant_context
from django_tenants.utils import schema_context

from customers.models import Client, Domain

User = get_user_model()


class CustomerManagementCommandTests(TestCase):
    def test_create_customer_tenant_command_creates_tenant_and_domain(self):
        out = StringIO()
        with schema_context('public'):
            call_command(
                'create_customer_tenant',
                schema='opsdemo',
                name='Ops Demo',
                domain='opsdemo.lvh.me',
                stdout=out,
            )

        tenant = Client.objects.get(schema_name='opsdemo')
        domain = Domain.objects.get(domain='opsdemo.lvh.me')

        self.assertEqual(tenant.name, 'Ops Demo')
        self.assertEqual(domain.tenant, tenant)
        self.assertTrue(domain.is_primary)

    def test_create_customer_tenant_admin_command_creates_superuser_in_tenant(self):
        tenant = Client.objects.create(schema_name='opsadmin', name='Ops Admin')
        Domain.objects.create(domain='opsadmin.lvh.me', tenant=tenant, is_primary=True)

        out = StringIO()

        call_command(
            'create_customer_tenant_admin',
            schema='opsadmin',
            username='admin',
            email='admin@opsadmin.com',
            password='StrongPass123!',
            stdout=out,
        )

        with tenant_context(tenant):
            user = User.objects.get(username='admin')
            self.assertEqual(user.email, 'admin@opsadmin.com')
            self.assertTrue(user.is_superuser)
            self.assertTrue(user.is_staff)
            self.assertTrue(user.check_password('StrongPass123!'))