from django.contrib.auth import get_user_model
from django.urls import reverse
from django_tenants.utils import tenant_context

from core.models import Contractor, Service, ServiceCategory
from core.tests.base import TenantTestCase

User = get_user_model()


class AdminCategoriesTests(TenantTestCase):
    def setUp(self):
        super().setUp()

        self.admin_user = self.create_tenant_superuser(
            username='admin',
            password='pass12345',
        )
        self.regular_user = self.create_tenant_user(
            username='user1',
            password='pass12345',
        )

    def test_admin_can_open_category_list(self):
        self.tenant_login(username='admin', password='pass12345')

        response = self.tenant_get(reverse('admin_category_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Категории услуг')

    def test_non_admin_cannot_open_category_list(self):
        self.tenant_login(username='user1', password='pass12345')

        response = self.tenant_get(reverse('admin_category_list'))

        self.assertEqual(response.status_code, 302)

    def test_admin_can_create_category(self):
        self.tenant_login(username='admin', password='pass12345')

        response = self.tenant_post(
            reverse('admin_category_create'),
            data={
                'name': 'Экскурсии',
                'sort_order': 10,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        if response.context and 'form' in response.context:
            self.assertFalse(response.context['form'].errors, response.context['form'].errors)

        with tenant_context(self.tenant):
            self.assertTrue(ServiceCategory.objects.filter(name='Экскурсии').exists())

    def test_admin_can_update_category(self):
        with tenant_context(self.tenant):
            category = ServiceCategory.objects.create(name='Транспорт', sort_order=1)

        self.tenant_login(username='admin', password='pass12345')

        response = self.tenant_post(
            reverse('admin_category_update', args=[category.id]),
            data={
                'name': 'Трансферы',
                'sort_order': 2,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        with tenant_context(self.tenant):
            category.refresh_from_db()
            self.assertEqual(category.name, 'Трансферы')
            self.assertEqual(category.sort_order, 2)

    def test_empty_category_can_be_deleted(self):
        with tenant_context(self.tenant):
            category = ServiceCategory.objects.create(name='Пустая категория', sort_order=1)

        self.tenant_login(username='admin', password='pass12345')

        response = self.tenant_post(
            reverse('admin_category_delete', args=[category.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        with tenant_context(self.tenant):
            self.assertFalse(ServiceCategory.objects.filter(id=category.id).exists())

    def test_category_with_services_cannot_be_deleted(self):
        with tenant_context(self.tenant):
            category = ServiceCategory.objects.create(name='Транспорт', sort_order=1)
            contractor = Contractor.objects.create(name='Поставщик')
            Service.objects.create(
                contractor=contractor,
                category=category,
                name='Трансфер',
                description='',
                cost_price='100.00',
                client_price='150.00',
                is_active=True,
                image_url='',
            )

        self.tenant_login(username='admin', password='pass12345')

        response = self.tenant_post(
            reverse('admin_category_delete', args=[category.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        with tenant_context(self.tenant):
            self.assertTrue(ServiceCategory.objects.filter(id=category.id).exists())

    def test_category_list_shows_usage_count(self):
        with tenant_context(self.tenant):
            category = ServiceCategory.objects.create(name='Транспорт', sort_order=1)
            contractor = Contractor.objects.create(name='Поставщик')
            Service.objects.create(
                contractor=contractor,
                category=category,
                name='Трансфер 1',
                description='',
                cost_price='100.00',
                client_price='150.00',
                is_active=True,
                image_url='',
            )
            Service.objects.create(
                contractor=contractor,
                category=category,
                name='Трансфер 2',
                description='',
                cost_price='100.00',
                client_price='150.00',
                is_active=True,
                image_url='',
            )

        self.tenant_login(username='admin', password='pass12345')
        response = self.tenant_get(reverse('admin_category_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2')