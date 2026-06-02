from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django_tenants.utils import tenant_context

from core.models import Estimate
from core.tests.base import TenantTestCase

User = get_user_model()


class EstimateCreateViewTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()

        with tenant_context(self.tenant):
            sales_group, _ = Group.objects.get_or_create(name='sales_manager')
            self.sales = User.objects.create_user(username='sales', password='pass')
            self.sales.groups.add(sales_group)

    def test_estimate_create_get_returns_200(self):
        self.tenant_login(username='sales', password='pass')
        response = self.tenant_get(reverse('estimate_create'))
        self.assertEqual(response.status_code, 200, getattr(response, 'url', None))
        self.assertContains(response, 'Создание сметы')

    def test_estimate_create_requires_contract_number(self):
        self.tenant_login(username='sales', password='pass')

        response = self.tenant_post(
            reverse('estimate_create'),
            data={
                'client_name': 'ООО Ромашка',
                'comment': 'Тест',
                'contract_number': '',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Укажите номер договора.')

        with tenant_context(self.tenant):
            self.assertEqual(Estimate.objects.count(), 0)

    def test_estimate_create_sets_first_number_within_contract(self):
        self.tenant_login(username='sales', password='pass')

        response = self.tenant_post(
            reverse('estimate_create'),
            data={
                'client_name': 'ООО Ромашка',
                'comment': 'Тест',
                'contract_number': 'DOG-001',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        with tenant_context(self.tenant):
            estimate = Estimate.objects.get()
            self.assertEqual(estimate.contract_number, 'DOG-001')
            self.assertEqual(estimate.contract_estimate_number, 1)

    def test_estimate_create_increments_number_within_same_contract(self):
        self.tenant_login(username='sales', password='pass')

        self.tenant_post(
            reverse('estimate_create'),
            data={
                'client_name': 'Клиент 1',
                'comment': '',
                'contract_number': 'DOG-001',
            },
            follow=True,
        )
        self.tenant_post(
            reverse('estimate_create'),
            data={
                'client_name': 'Клиент 2',
                'comment': '',
                'contract_number': 'DOG-001',
            },
            follow=True,
        )

        with tenant_context(self.tenant):
            estimates = list(Estimate.objects.filter(contract_number='DOG-001').order_by('contract_estimate_number'))
            self.assertEqual(len(estimates), 2)
            self.assertEqual(estimates[0].contract_estimate_number, 1)
            self.assertEqual(estimates[1].contract_estimate_number, 2)

    def test_estimate_create_starts_numbering_from_one_for_new_contract(self):
        self.tenant_login(username='sales', password='pass')

        self.tenant_post(
            reverse('estimate_create'),
            data={
                'client_name': 'Клиент 1',
                'comment': '',
                'contract_number': 'DOG-001',
            },
            follow=True,
        )
        self.tenant_post(
            reverse('estimate_create'),
            data={
                'client_name': 'Клиент 2',
                'comment': '',
                'contract_number': 'DOG-002',
            },
            follow=True,
        )

        with tenant_context(self.tenant):
            first = Estimate.objects.get(contract_number='DOG-001')
            second = Estimate.objects.get(contract_number='DOG-002')

            self.assertEqual(first.contract_estimate_number, 1)
            self.assertEqual(second.contract_estimate_number, 1)