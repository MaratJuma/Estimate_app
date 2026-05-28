from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AdminUsersTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='pass12345',
            is_superuser=True,
            is_staff=True,
        )
        self.sales_group, _ = Group.objects.get_or_create(name='sales_manager')
        self.production_group, _ = Group.objects.get_or_create(name='production_manager')

        self.sales_user = User.objects.create_user(
            username='sales1',
            password='pass12345',
            first_name='Иван',
            last_name='Иванов',
        )
        self.sales_user.groups.add(self.sales_group)

    def test_admin_can_open_user_list(self):
        self.client.login(username='admin', password='pass12345')
        response = self.client.get(reverse('admin_user_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пользователи')

    def test_non_admin_cannot_open_user_list(self):
        self.client.login(username='sales1', password='pass12345')
        response = self.client.get(reverse('admin_user_list'))

        self.assertEqual(response.status_code, 302)

    def test_admin_can_create_sales_user(self):
        self.client.login(username='admin', password='pass12345')

        response = self.client.post(
            reverse('admin_user_create'),
            data={
                'username': 'sales2',
                'first_name': 'Петр',
                'last_name': 'Петров',
                'is_active': 'on',
                'role': 'sales_manager',
                'password1': 'pass12345',
                'password2': 'pass12345',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        created_user = User.objects.get(username='sales2')
        self.assertTrue(created_user.groups.filter(name='sales_manager').exists())
        self.assertFalse(created_user.is_superuser)

    def test_admin_can_create_admin_user(self):
        self.client.login(username='admin', password='pass12345')

        self.client.post(
            reverse('admin_user_create'),
            data={
                'username': 'admin2',
                'first_name': 'Admin',
                'last_name': 'Two',
                'is_active': 'on',
                'role': 'admin',
                'password1': 'pass12345',
                'password2': 'pass12345',
            },
            follow=True,
        )

        created_user = User.objects.get(username='admin2')
        self.assertTrue(created_user.is_superuser)
        self.assertTrue(created_user.is_staff)

    def test_admin_can_update_user_role(self):
        self.client.login(username='admin', password='pass12345')

        response = self.client.post(
            reverse('admin_user_update', args=[self.sales_user.id]),
            data={
                'username': 'sales1',
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'is_active': 'on',
                'role': 'production_manager',
                'new_password1': '',
                'new_password2': '',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.sales_user.refresh_from_db()

        self.assertTrue(self.sales_user.groups.filter(name='production_manager').exists())
        self.assertFalse(self.sales_user.groups.filter(name='sales_manager').exists())
        self.assertFalse(self.sales_user.is_superuser)

    def test_admin_can_change_user_password(self):
        self.client.login(username='admin', password='pass12345')

        self.client.post(
            reverse('admin_user_update', args=[self.sales_user.id]),
            data={
                'username': 'sales1',
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'is_active': 'on',
                'role': 'sales_manager',
                'new_password1': 'newpass12345',
                'new_password2': 'newpass12345',
            },
            follow=True,
        )

        self.sales_user.refresh_from_db()
        self.assertTrue(self.sales_user.check_password('newpass12345'))

    def test_admin_cannot_delete_self(self):
        self.client.login(username='admin', password='pass12345')

        response = self.client.post(
            reverse('admin_user_delete', args=[self.admin_user.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(id=self.admin_user.id).exists())

    def test_admin_cannot_delete_last_admin(self):
        other_admin = User.objects.create_user(
            username='admin2',
            password='pass12345',
            is_superuser=True,
            is_staff=True,
        )

        other_admin.delete()
        self.client.login(username='admin', password='pass12345')

        response = self.client.post(
            reverse('admin_user_delete', args=[self.admin_user.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(id=self.admin_user.id).exists())

    def test_admin_can_delete_other_user(self):
        self.client.login(username='admin', password='pass12345')

        response = self.client.post(
            reverse('admin_user_delete', args=[self.sales_user.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(id=self.sales_user.id).exists())