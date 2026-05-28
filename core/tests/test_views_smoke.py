from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse


class ViewSmokeTestCase(TestCase):
    def setUp(self):
        self.sales = User.objects.create_user(username='sales', password='pass')
        sales_group, _ = Group.objects.get_or_create(name='sales_manager')
        self.sales.groups.add(sales_group)

    def test_home_page_opens(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_estimate_list_opens_for_sales_manager(self):
        self.client.force_login(self.sales)
        response = self.client.get(reverse('estimate_list'))
        self.assertEqual(response.status_code, 200)

    def test_estimate_create_opens_for_sales_manager(self):
        self.client.force_login(self.sales)
        response = self.client.get(reverse('estimate_create'))
        self.assertEqual(response.status_code, 200)