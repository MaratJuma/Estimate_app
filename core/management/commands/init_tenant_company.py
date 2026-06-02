# core/management/commands/init_tenant_company.py
from django.core.management.base import BaseCommand
from django_tenants.utils import tenant_context
from customers.models import Client
from core.models import CompanyProfile


class Command(BaseCommand):
    help = 'Инициализирует профиль компании для tenant sakhtravel'

    def handle(self, *args, **options):
        try:
            tenant = Client.objects.get(schema_name='sakhtravel')
        except Client.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('❌ Tenant "sakhtravel" не найден')
            )
            return

        with tenant_context(tenant):
            profile, created = CompanyProfile.objects.get_or_create(
                id=1,
                defaults={
                    'name': 'SAKHTRAVEL',
                    'tagline': 'Объединяя мечты',
                    'phone': '+7 (934) 477-30-08',
                    'email': 'go@sakhtravel.com',
                    'site': 'www.sakhtravel.com',
                    'address': 'г. Южно-Сахалинск, ул. Есенина, 1',
                    'manager_title': 'Менеджер проекта',
                    'manager_name': '',
                }
            )

            if not created:
                profile.name = 'SAKHTRAVEL'
                profile.tagline = 'Объединяя мечты'
                profile.phone = '+7 (934) 477-30-08'
                profile.email = 'go@sakhtravel.com'
                profile.site = 'www.sakhtravel.com'
                profile.address = 'г. Южно-Сахалинск, ул. Есенина, 1'
                profile.manager_title = 'Менеджер проекта'
                profile.save()
                self.stdout.write(
                    self.style.WARNING('⚠️ Профиль обновлён')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ Профиль создан')
                )

            self.stdout.write(
                self.style.NOTICE(f'📌 Профиль: {profile.id} — {profile.name}')
            )