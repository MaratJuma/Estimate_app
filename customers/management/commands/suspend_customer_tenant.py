# customers/management/commands/suspend_customer_tenant.py
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import tenant_context
from customers.models import Client


class Command(BaseCommand):
    help = 'Временно блокирует tenant по schema_name'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            required=True,
            help='Имя schema_name tenant'  # например, 'testops'
        )

    def handle(self, *args, **options):
        schema_name = options['schema']

        try:
            tenant = Client.objects.get(schema_name=schema_name)
        except Client.DoesNotExist:
            raise CommandError(f'Tenant с schema_name="{schema_name}" не найден.')

        # Вариант 1: просто деактивировать tenant (если есть поле is_active)
        if hasattr(tenant, 'is_active'):
            tenant.is_active = False
            tenant.save()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Tenant "{schema_name}" заблокирован. (is_active=False)')
            )
            return

        # Вариант 2: временно переименовать schema — если нужно полностью исключить
        # (менее предпочтительно, так как ломает связи)

        # Вариант 3: просто вывести предупреждение — если логика suspend реализована elsewhere
        self.stdout.write(
            self.style.WARNING(f'⚠️ Tenant "{schema_name}" найден, но не поддерживает is_active.')
        )