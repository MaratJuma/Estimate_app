from django.contrib.auth.models import AnonymousUser
from django.template.response import TemplateResponse
from django.test import RequestFactory, TestCase

from customers.middleware import SuspendedTenantMiddleware
from customers.models import Client, Domain


class SuspendedTenantMiddlewareTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.active_tenant = Client.objects.create(
            schema_name='active1',
            name='Active Tenant',
            is_active=True,
        )
        Domain.objects.create(
            domain='active1.lvh.me',
            tenant=cls.active_tenant,
            is_primary=True,
        )

        cls.suspended_tenant = Client.objects.create(
            schema_name='suspended1',
            name='Suspended Tenant',
            is_active=False,
        )
        Domain.objects.create(
            domain='suspended1.lvh.me',
            tenant=cls.suspended_tenant,
            is_primary=True,
        )

    def get_response(self, request):
        return TemplateResponse(request, 'core/base.html', {})

    def test_active_tenant_is_not_blocked(self):
        request = RequestFactory().get('/')
        request.tenant = self.active_tenant
        request.user = AnonymousUser()

        middleware = SuspendedTenantMiddleware(self.get_response)
        response = middleware(request)

        self.assertNotEqual(response.status_code, 403)

    def test_suspended_tenant_is_blocked(self):
        request = RequestFactory().get('/')
        request.tenant = self.suspended_tenant
        request.user = AnonymousUser()

        middleware = SuspendedTenantMiddleware(self.get_response)
        response = middleware(request)

        self.assertEqual(response.status_code, 403)

    def test_public_schema_is_not_blocked(self):
        request = RequestFactory().get('/')

        public_like_tenant = type('Tenant', (), {
            'schema_name': 'public',
            'is_active': False,
            'name': 'Public',
        })()

        request.tenant = public_like_tenant
        request.user = AnonymousUser()

        middleware = SuspendedTenantMiddleware(self.get_response)
        response = middleware(request)

        self.assertNotEqual(response.status_code, 403)