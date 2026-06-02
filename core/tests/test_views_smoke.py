from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django_tenants.utils import tenant_context

from core.tests.base import TenantTestCase

User = get_user_model()


class ViewSmokeTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()

        with tenant_context(self.tenant):
            self.sales = User.objects.create_user(username='sales', password='pass')
            sales_group, _ = Group.objects.get_or_create(name='sales_manager')
            self.sales.groups.add(sales_group)

    def test_home_page_opens(self):
        self.tenant_login(username='sales', password='pass')
        response = self.tenant_get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_estimate_list_opens_for_sales_manager(self):
        self.tenant_login(username='sales', password='pass')
        response = self.tenant_get(reverse('estimate_list'))
        self.assertEqual(response.status_code, 200)

    def test_estimate_create_opens_for_sales_manager(self):
        self.tenant_login(username='sales', password='pass')
        response = self.tenant_get(reverse('estimate_create'))
        self.assertEqual(response.status_code, 200)

    def test_estimate_create_post_works_for_sales_manager(self):
        self.tenant_login(username='sales', password='pass')
        response = self.tenant_post(
            reverse('estimate_create'),
            data={
                'client_name': 'ООО Ромашка',
                'comment': 'Тест',
                'contract_number': 'DOG-SMOKE-001',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)