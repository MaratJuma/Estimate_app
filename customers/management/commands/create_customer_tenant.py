from django.core.management.base import BaseCommand, CommandError

from customers.models import Client, Domain


class Command(BaseCommand):
    help = "Создаёт tenant и primary domain."

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True, help='Имя schema, например: acme')
        parser.add_argument('--name', required=True, help='Название компании')
        parser.add_argument('--domain', required=True, help='Primary domain, например: acme.sistemasmet.online')

    def handle(self, *args, **options):
        schema_name = options['schema'].strip().lower()
        company_name = options['name'].strip()
        domain_name = options['domain'].strip().lower()

        if Client.objects.filter(schema_name=schema_name).exists():
            raise CommandError(f'Tenant со schema "{schema_name}" уже существует.')

        if Domain.objects.filter(domain=domain_name).exists():
            raise CommandError(f'Domain "{domain_name}" уже существует.')

        tenant = Client.objects.create(
            schema_name=schema_name,
            name=company_name,
        )

        Domain.objects.create(
            domain=domain_name,
            tenant=tenant,
            is_primary=True,
        )

        self.stdout.write(self.style.SUCCESS(
            f'Tenant создан: schema={tenant.schema_name}, name="{tenant.name}", domain={domain_name}'
        ))