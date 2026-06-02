from django.contrib.auth import get_user_model
from django_tenants.test.cases import TenantTestCase as DjangoTenantsTenantTestCase
from django_tenants.test.client import TenantClient
from django_tenants.utils import tenant_context

from customers.models import Domain

User = get_user_model()


class TenantTestCase(DjangoTenantsTenantTestCase):
    @staticmethod
    def get_test_schema_name():
        return 'testtenant'

    @staticmethod
    def get_test_tenant_domain():
        return 'testtenant.lvh.me'

    def setUp(self):
        super().setUp()

        Domain.objects.get_or_create(
            domain=self.get_test_tenant_domain(),
            tenant=self.tenant,
            defaults={'is_primary': True},
        )

        self.client = TenantClient(self.tenant)

    def tenant_context(self):
        return tenant_context(self.tenant)

    def create_tenant_user(self, username, password, **extra_fields):
        with tenant_context(self.tenant):
            return User.objects.create_user(
                username=username,
                password=password,
                **extra_fields,
            )

    def create_tenant_superuser(self, username, password, **extra_fields):
        with tenant_context(self.tenant):
            return User.objects.create_superuser(
                username=username,
                password=password,
                **extra_fields,
            )

    def tenant_login(self, username, password):
        return self.client.login(username=username, password=password)

    def tenant_get(self, url, **kwargs):
        return self.client.get(url, **kwargs)

    def tenant_post(self, url, data=None, **kwargs):
        return self.client.post(url, data=data or {}, **kwargs)