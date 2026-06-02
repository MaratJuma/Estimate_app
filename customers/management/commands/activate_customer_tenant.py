from django.core.management.base import BaseCommand, CommandError

from customers.models import Client


class Command(BaseCommand):
    help = "Включает tenant (ставит is_active=True)."

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True, help='Schema tenant-а, например: acme')

    def handle(self, *args, **options):
        schema_name = options['schema'].strip().lower()

        try:
            tenant = Client.objects.get(schema_name=schema_name)
        except Client.DoesNotExist:
            raise CommandError(f'Tenant со schema "{schema_name}" не найден.')

        if tenant.is_active:
            self.stdout.write(f'Tenant "{schema_name}" уже активен.')
            return

        tenant.is_active = True
        tenant.save(update_fields=['is_active'])

        self.stdout.write(self.style.SUCCESS(
            f'✅ Tenant "{schema_name}" активирован (is_active=True).'
        ))