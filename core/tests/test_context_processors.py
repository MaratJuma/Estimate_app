from django.test import RequestFactory
from django_tenants.utils import tenant_context

from core.context_processors import company_branding
from core.models import CompanyProfile
from core.tests.base import TenantTestCase


class CompanyBrandingContextProcessorTests(TenantTestCase):
    def test_returns_fallback_values_when_profile_missing(self):
        request = RequestFactory().get('/')

        with tenant_context(self.tenant):
            context = company_branding(request)

        self.assertEqual(context['company_name'], 'Компания')
        self.assertEqual(context['company_tagline'], '')
        self.assertIsNone(context['company_logo_url'])
        self.assertEqual(context['platform_name'], 'SistemaSmet')

    def test_returns_profile_values_when_profile_exists(self):
        request = RequestFactory().get('/')

        with tenant_context(self.tenant):
            CompanyProfile.objects.create(
                name='Acme Travel',
                tagline='Лучшие сметы',
            )
            context = company_branding(request)

        self.assertEqual(context['company_name'], 'Acme Travel')
        self.assertEqual(context['company_tagline'], 'Лучшие сметы')
        self.assertEqual(context['platform_name'], 'SistemaSmet')