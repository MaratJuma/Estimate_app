from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django_tenants.utils import tenant_context

from core.permissions import (
    is_admin,
    is_production_manager,
    is_sales_manager,
    can_view_estimates,
    can_edit_estimates,
    can_approve_estimates,
    can_manage_services,
    can_manage_contractors,
)
from core.tests.base import TenantTestCase

User = get_user_model()


class PermissionsTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()

        with tenant_context(self.tenant):
            self.admin = User.objects.create_user(
                username='admin',
                password='pass',
                is_superuser=True,
            )
            self.production = User.objects.create_user(
                username='production',
                password='pass',
            )
            self.sales = User.objects.create_user(
                username='sales',
                password='pass',
            )
            self.regular = User.objects.create_user(
                username='regular',
                password='pass',
            )

            production_group, _ = Group.objects.get_or_create(name='production_manager')
            sales_group, _ = Group.objects.get_or_create(name='sales_manager')

            self.production.groups.add(production_group)
            self.sales.groups.add(sales_group)

    def test_admin_has_full_access(self):
        self.assertTrue(is_admin(self.admin))
        self.assertTrue(can_view_estimates(self.admin))
        self.assertTrue(can_edit_estimates(self.admin))
        self.assertTrue(can_approve_estimates(self.admin))
        self.assertTrue(can_manage_services(self.admin))
        self.assertTrue(can_manage_contractors(self.admin))

    def test_production_manager_permissions(self):
        self.assertTrue(is_production_manager(self.production))
        self.assertTrue(can_view_estimates(self.production))
        self.assertFalse(can_edit_estimates(self.production))
        self.assertTrue(can_approve_estimates(self.production))
        self.assertTrue(can_manage_services(self.production))
        self.assertTrue(can_manage_contractors(self.production))

    def test_sales_manager_permissions(self):
        self.assertTrue(is_sales_manager(self.sales))
        self.assertTrue(can_view_estimates(self.sales))
        self.assertTrue(can_edit_estimates(self.sales))
        self.assertFalse(can_approve_estimates(self.sales))
        self.assertFalse(can_manage_services(self.sales))
        self.assertFalse(can_manage_contractors(self.sales))

    def test_regular_user_has_no_business_permissions(self):
        self.assertFalse(can_view_estimates(self.regular))
        self.assertFalse(can_edit_estimates(self.regular))
        self.assertFalse(can_approve_estimates(self.regular))
        self.assertFalse(can_manage_services(self.regular))
        self.assertFalse(can_manage_contractors(self.regular))