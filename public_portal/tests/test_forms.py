from django.test import TestCase

from customers.models import Client
from public_portal.forms import PublicTenantRegistrationForm
from django_tenants.utils import schema_context


class PublicTenantRegistrationFormTests(TestCase):
    def get_valid_data(self, **overrides):
        data = {
            'company_name': 'Demo2 Company',
            'subdomain': 'demo2',
            'phone': '+79990000000',
            'company_email': 'info@demo.com',
            'website': 'https://demo2.com',
            'address': 'Moscow',
            'admin_username': 'admin',
            'admin_email': 'admin@demo2.com',
            'password1': 'admin12345',
            'password2': 'admin12345',
        }
        data.update(overrides)
        return data

    def test_form_is_valid_with_correct_data(self):
        form = PublicTenantRegistrationForm(data=self.get_valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_reserved_subdomain(self):
        form = PublicTenantRegistrationForm(data=self.get_valid_data(subdomain='admin'))
        self.assertFalse(form.is_valid())
        self.assertIn('subdomain', form.errors)

    def test_form_rejects_duplicate_subdomain(self):
        with schema_context('public'):
            Client.objects.create(schema_name='demo2', name='Existing Demo2')

        form = PublicTenantRegistrationForm(data=self.get_valid_data(subdomain='demo2'))
        self.assertFalse(form.is_valid())
        self.assertIn('subdomain', form.errors)

    def test_form_rejects_password_mismatch(self):
        form = PublicTenantRegistrationForm(
            data=self.get_valid_data(password2='AnotherPass123!')
        )
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_form_rejects_invalid_subdomain_chars(self):
        form = PublicTenantRegistrationForm(data=self.get_valid_data(subdomain='demo2_ru'))
        self.assertFalse(form.is_valid())
        self.assertIn('subdomain', form.errors)

    def test_form_rejects_subdomain_with_edge_hyphen(self):
        form = PublicTenantRegistrationForm(data=self.get_valid_data(subdomain='-demo2'))
        self.assertFalse(form.is_valid())
        self.assertIn('subdomain', form.errors)