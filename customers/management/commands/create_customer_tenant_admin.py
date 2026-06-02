from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import tenant_context

from customers.models import Client

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт superuser/admin внутри tenant schema."

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True, help='Schema tenant-а, например: acme')
        parser.add_argument('--username', required=True, help='Логин администратора')
        parser.add_argument('--email', required=True, help='E-mail администратора')
        parser.add_argument('--password', required=True, help='Пароль администратора')

    def handle(self, *args, **options):
        schema_name = options['schema'].strip().lower()
        username = options['username'].strip()
        email = options['email'].strip()
        password = options['password']

        try:
            tenant = Client.objects.get(schema_name=schema_name)
        except Client.DoesNotExist:
            raise CommandError(f'Tenant со schema "{schema_name}" не найден.')

        with tenant_context(tenant):
            if User.objects.filter(username=username).exists():
                raise CommandError(
                    f'Пользователь "{username}" уже существует в tenant "{schema_name}".'
                )

            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )

        self.stdout.write(self.style.SUCCESS(
            f'Администратор "{user.username}" создан в tenant "{schema_name}".'
        ))