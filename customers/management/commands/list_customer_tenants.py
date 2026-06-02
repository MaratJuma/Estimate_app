from django.core.management.base import BaseCommand

from customers.models import Client


class Command(BaseCommand):
    help = "Показывает список tenant-ов."

    def handle(self, *args, **options):
        tenants = Client.objects.all().order_by('created_at')

        if not tenants.exists():
            self.stdout.write('Tenant-ов пока нет.')
            return

        for tenant in tenants:
            primary_domain = tenant.domains.filter(is_primary=True).first()
            domain_value = primary_domain.domain if primary_domain else '—'

            self.stdout.write(
                f'schema={tenant.schema_name} | '
                f'name="{tenant.name}" | '
                f'domain={domain_value} | '
                f'is_active={tenant.is_active} | '
                f'created_at={tenant.created_at:%Y-%m-%d %H:%M:%S}'
            )