from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django_tenants.utils import tenant_context

from core.models import Contractor, Estimate, EstimateItem, Service, ServiceCategory
from core.services.estimates import create_estimate_with_first_day
from core.tests.base import TenantTestCase

User = get_user_model()


class EstimateOwnershipTests(TenantTestCase):
    def setUp(self):
        super().setUp()

        with tenant_context(self.tenant):
            self.sales_group, _ = Group.objects.get_or_create(name='sales_manager')

            self.owner = User.objects.create_user(
                username='owner',
                password='pass12345',
                first_name='Иван',
                last_name='Иванов',
            )
            self.owner.groups.add(self.sales_group)

            self.other_manager = User.objects.create_user(
                username='other',
                password='pass12345',
                first_name='Петр',
                last_name='Петров',
            )
            self.other_manager.groups.add(self.sales_group)

            self.admin_user = User.objects.create_user(
                username='admin',
                password='pass12345',
                is_superuser=True,
                is_staff=True,
            )

            self.estimate = create_estimate_with_first_day(
                client_name='ООО Ромашка',
                comment='Тест',
                contract_number='DOG-001',
                user=self.owner,
            )

            self.category = ServiceCategory.objects.create(name='Транспорт', sort_order=1)
            self.contractor = Contractor.objects.create(name='Поставщик')
            self.service = Service.objects.create(
                contractor=self.contractor,
                category=self.category,
                name='Трансфер',
                description='',
                cost_price='100.00',
                client_price='150.00',
                is_active=True,
                image_url='',
            )

    def test_owner_can_open_estimate_update(self):
        self.tenant_login(username='owner', password='pass12345')

        response = self.tenant_get(reverse('estimate_update', args=[self.estimate.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Редактирование сметы')

    def test_other_manager_cannot_open_estimate_update(self):
        self.tenant_login(username='other', password='pass12345')

        response = self.tenant_get(
            reverse('estimate_update', args=[self.estimate.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'У вас нет прав на редактирование этой сметы.')

    def test_admin_can_open_estimate_update(self):
        self.tenant_login(username='admin', password='pass12345')

        response = self.tenant_get(reverse('estimate_update', args=[self.estimate.id]))

        self.assertEqual(response.status_code, 200)

    def test_owner_can_delete_empty_estimate(self):
        self.tenant_login(username='owner', password='pass12345')

        response = self.tenant_post(
            reverse('estimate_delete', args=[self.estimate.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

    def test_owner_cannot_delete_estimate_with_items(self):
        with tenant_context(self.tenant):
            day = self.estimate.days.first()
            EstimateItem.objects.create(
                estimate_day=day,
                service=self.service,
                qty='1.00',
                cost_price='100.00',
                client_price='150.00',
                total_cost='100.00',
                total_client='150.00',
            )

        self.tenant_login(username='owner', password='pass12345')

        response = self.tenant_post(
            reverse('estimate_delete', args=[self.estimate.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        with tenant_context(self.tenant):
            self.assertTrue(Estimate.objects.filter(id=self.estimate.id).exists())

    def test_other_manager_cannot_delete_foreign_estimate(self):
        self.tenant_login(username='other', password='pass12345')

        response = self.tenant_post(
            reverse('estimate_delete', args=[self.estimate.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        with tenant_context(self.tenant):
            self.assertTrue(Estimate.objects.filter(id=self.estimate.id).exists())

    def test_any_sales_manager_can_duplicate_estimate(self):
        self.tenant_login(username='other', password='pass12345')

        response = self.tenant_post(
            reverse('estimate_duplicate', args=[self.estimate.id]),
            data={'contract_number': 'DOG-001'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'успешно скопирована')

    def test_duplicated_estimate_belongs_to_duplicator(self):
        self.tenant_login(username='other', password='pass12345')

        self.tenant_post(
            reverse('estimate_duplicate', args=[self.estimate.id]),
            data={'contract_number': 'DOG-001'},
            follow=True,
        )

        with tenant_context(self.tenant):
            duplicated = Estimate.objects.order_by('-id').first()

            self.assertNotEqual(duplicated.id, self.estimate.id)
            self.assertEqual(duplicated.created_by, self.other_manager)
            self.assertEqual(duplicated.manager_name, 'Петр Петров')
            self.assertEqual(duplicated.contract_number, 'DOG-001')
            self.assertEqual(duplicated.contract_estimate_number, 2)

    def test_duplicate_can_use_new_contract_number(self):
        self.tenant_login(username='other', password='pass12345')

        self.tenant_post(
            reverse('estimate_duplicate', args=[self.estimate.id]),
            data={'contract_number': 'DOG-999'},
            follow=True,
        )

        with tenant_context(self.tenant):
            duplicated = Estimate.objects.order_by('-id').first()
            self.assertEqual(duplicated.contract_number, 'DOG-999')
            self.assertEqual(duplicated.contract_estimate_number, 1)

    def test_regular_update_cannot_change_contract_number(self):
        self.tenant_login(username='owner', password='pass12345')

        response = self.tenant_post(
            reverse('estimate_update', args=[self.estimate.id]),
            data={
                'client_name': self.estimate.client_name,
                'comment': 'Обновлённый комментарий',
                'contract_number': 'DOG-CHANGED',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        with tenant_context(self.tenant):
            self.estimate.refresh_from_db()
            self.assertEqual(self.estimate.contract_number, 'DOG-001')
            self.assertEqual(self.estimate.contract_estimate_number, 1)
            self.assertEqual(self.estimate.comment, 'Обновлённый комментарий')