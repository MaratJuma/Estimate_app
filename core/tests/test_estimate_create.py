from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse


class EstimateCreateViewTestCase(TestCase):
    def setUp(self):
        self.sales = User.objects.create_user(username='sales', password='pass')
        sales_group, _ = Group.objects.get_or_create(name='sales_manager')
        self.sales.groups.add(sales_group)

    def test_estimate_create_get_returns_200(self):
        self.client.force_login(self.sales)
        response = self.client.get(reverse('estimate_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Создание сметы')