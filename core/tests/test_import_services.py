from decimal import Decimal
from io import BytesIO

from openpyxl import Workbook
from django_tenants.utils import tenant_context

from core.models import Contractor, Service, ServiceCategory
from core.services.imports import (
    import_services_from_excel,
    preview_services_import,
)
from core.tests.base import TenantTestCase


EXPECTED_HEADERS = [
    'Подрядчик',
    'Комментарий к подрядчику',
    'Телефон',
    'E-mail',
    'Категория услуги',
    'Услуга',
    'Комментарий к услуге',
    'Себестоимость',
    'Цена',
    'Медиа',
]


def build_excel_file(rows, headers=None):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(headers or EXPECTED_HEADERS)

    for row in rows:
        sheet.append(row)

    file_obj = BytesIO()
    workbook.save(file_obj)
    file_obj.seek(0)
    return file_obj


class ImportServicesTests(TenantTestCase):
    def test_preview_does_not_write_to_database(self):
        file_obj = build_excel_file([
            [
                'Ромашка', 'VIP подрядчик', '+79990000001', 'info1@example.com',
                'Транспорт', 'Трансфер аэропорт', 'Ночной тариф',
                '1000', '1500', 'https://example.com/1'
            ],
        ])

        with tenant_context(self.tenant):
            result = preview_services_import(file_obj)

            self.assertTrue(result['dry_run'])
            self.assertEqual(result['rows_processed'], 1)
            self.assertEqual(result['errors'], [])

            self.assertEqual(Contractor.objects.count(), 0)
            self.assertEqual(ServiceCategory.objects.count(), 0)
            self.assertEqual(Service.objects.count(), 0)

    def test_import_writes_to_database(self):
        file_obj = build_excel_file([
            [
                'Ромашка', 'VIP подрядчик', '+79990000001', 'info1@example.com',
                'Транспорт', 'Трансфер аэропорт', 'Ночной тариф',
                '1000', '1500', 'https://example.com/1'
            ],
        ])

        with tenant_context(self.tenant):
            result = import_services_from_excel(file_obj)

            self.assertFalse(result['dry_run'])
            self.assertEqual(result['rows_processed'], 1)
            self.assertEqual(result['errors'], [])

            self.assertEqual(Contractor.objects.count(), 1)
            self.assertEqual(ServiceCategory.objects.count(), 1)
            self.assertEqual(Service.objects.count(), 1)

            contractor = Contractor.objects.get()
            category = ServiceCategory.objects.get()
            service = Service.objects.get()

            self.assertEqual(contractor.name, 'Ромашка')
            self.assertEqual(contractor.notes, 'VIP подрядчик')
            self.assertEqual(contractor.phone, '+79990000001')
            self.assertEqual(contractor.email, 'info1@example.com')

            self.assertEqual(category.name, 'Транспорт')

            self.assertEqual(service.name, 'Трансфер аэропорт')
            self.assertEqual(service.description, 'Ночной тариф')
            self.assertEqual(service.cost_price, Decimal('1000'))
            self.assertEqual(service.client_price, Decimal('1500'))
            self.assertEqual(service.image_url, 'https://example.com/1')
            self.assertEqual(service.contractor, contractor)
            self.assertEqual(service.category, category)

    def test_import_with_context_rows_for_contractor_and_category(self):
        file_obj = build_excel_file([
            ['Ромашка', 'VIP подрядчик', '+79990000001', 'info1@example.com', 'Транспорт', '', '', '', '', ''],
            ['', '', '', '', '', 'Трансфер аэропорт', 'Ночной тариф', '1000', '1500', 'https://example.com/1'],
            ['', '', '', '', '', 'Трансфер вокзал', 'Дневной тариф', '900', '1400', 'https://example.com/2'],
            ['', '', '', '', 'Экскурсии', '', '', '', '', ''],
            ['', '', '', '', '', 'Обзорная экскурсия', '5 часов', '3000', '5000', 'https://example.com/3'],
        ])

        with tenant_context(self.tenant):
            result = import_services_from_excel(file_obj)

            self.assertEqual(result['errors'], [])
            self.assertEqual(result['rows_processed'], 5)

            self.assertEqual(Contractor.objects.count(), 1)
            self.assertEqual(ServiceCategory.objects.count(), 2)
            self.assertEqual(Service.objects.count(), 3)

            contractor = Contractor.objects.get()
            self.assertEqual(contractor.name, 'Ромашка')

            transport = ServiceCategory.objects.get(name='Транспорт')
            excursions = ServiceCategory.objects.get(name='Экскурсии')

            self.assertTrue(Service.objects.filter(
                contractor=contractor,
                category=transport,
                name='Трансфер аэропорт',
            ).exists())

            self.assertTrue(Service.objects.filter(
                contractor=contractor,
                category=transport,
                name='Трансфер вокзал',
            ).exists())

            self.assertTrue(Service.objects.filter(
                contractor=contractor,
                category=excursions,
                name='Обзорная экскурсия',
            ).exists())

    def test_import_updates_existing_service(self):
        with tenant_context(self.tenant):
            contractor = Contractor.objects.create(
                name='Ромашка',
                notes='Старый комментарий',
                phone='111',
                email='old@example.com',
            )
            category = ServiceCategory.objects.create(name='Транспорт')
            service = Service.objects.create(
                contractor=contractor,
                category=category,
                name='Трансфер аэропорт',
                description='Старое описание',
                cost_price=Decimal('800'),
                client_price=Decimal('1200'),
                image_url='https://example.com/old',
                is_active=False,
            )

        file_obj = build_excel_file([
            [
                'Ромашка', 'Новый комментарий', '+79990000002', 'new@example.com',
                'Транспорт', 'Трансфер аэропорт', 'Новое описание',
                '1000', '1500', 'https://example.com/new'
            ],
        ])

        with tenant_context(self.tenant):
            result = import_services_from_excel(file_obj)

            self.assertEqual(result['errors'], [])
            self.assertEqual(result['contractors_updated'], 1)
            self.assertEqual(result['services_updated'], 1)

            contractor.refresh_from_db()
            service.refresh_from_db()

            self.assertEqual(contractor.notes, 'Новый комментарий')
            self.assertEqual(contractor.phone, '+79990000002')
            self.assertEqual(contractor.email, 'new@example.com')

            self.assertEqual(service.description, 'Новое описание')
            self.assertEqual(service.cost_price, Decimal('1000'))
            self.assertEqual(service.client_price, Decimal('1500'))
            self.assertEqual(service.image_url, 'https://example.com/new')
            self.assertTrue(service.is_active)

    def test_invalid_headers_raise_error(self):
        file_obj = build_excel_file(
            rows=[
                ['Ромашка', 'Комментарий', '+79990000001', 'info@example.com', 'Транспорт', 'Трансфер', 'Описание', '1000', '1500', 'https://example.com/1']
            ],
            headers=[
                'Категория',
                'Услуга',
                'комментарий по услуге',
                'Подрядчик',
                'комментарий по подрядчику',
                'Себестоимость',
                'Стоимость',
                'Телефон',
                'e-mail',
                'ссылка на медиа',
            ],
        )

        with tenant_context(self.tenant):
            with self.assertRaisesMessage(ValueError, 'Неверная структура файла'):
                preview_services_import(file_obj)

    def test_invalid_numeric_row_goes_to_errors(self):
        file_obj = build_excel_file([
            [
                'Ромашка', 'Комментарий', '+79990000001', 'info@example.com',
                'Транспорт', 'Трансфер аэропорт', 'Описание',
                'не число', '1500', 'https://example.com/1'
            ],
        ])

        with tenant_context(self.tenant):
            result = preview_services_import(file_obj)

            self.assertEqual(result['rows_processed'], 0)
            self.assertEqual(len(result['errors']), 1)
            self.assertEqual(result['errors'][0]['row'], 2)
            self.assertIn('Некорректное числовое значение', result['errors'][0]['message'])

    def test_skip_empty_rows(self):
        file_obj = build_excel_file([
            [
                'Ромашка', 'Комментарий', '+79990000001', 'info@example.com',
                'Транспорт', 'Трансфер аэропорт', 'Описание',
                '1000', '1500', 'https://example.com/1'
            ],
            ['', '', '', '', '', '', '', '', '', ''],
            [
                '', '', '', '', '',
                'Трансфер вокзал', 'Описание 2',
                '900', '1400', 'https://example.com/2'
            ],
        ])

        with tenant_context(self.tenant):
            result = preview_services_import(file_obj)

            self.assertEqual(result['rows_processed'], 2)
            self.assertEqual(result['rows_skipped'], 1)
            self.assertEqual(result['errors'], [])

    def test_no_duplicate_categories_in_single_file(self):
        file_obj = build_excel_file([
            ['Ромашка', 'Комментарий', '+79990000001', 'info@example.com', 'Транспорт', '', '', '', '', ''],
            ['', '', '', '', '', 'Трансфер аэропорт', 'Описание 1', '1000', '1500', 'https://example.com/1'],
            ['', '', '', '', 'Транспорт', '', '', '', '', ''],
            ['', '', '', '', '', 'Трансфер вокзал', 'Описание 2', '900', '1400', 'https://example.com/2'],
        ])

        with tenant_context(self.tenant):
            result = import_services_from_excel(file_obj)

            self.assertEqual(result['errors'], [])
            self.assertEqual(ServiceCategory.objects.count(), 1)
            self.assertEqual(Service.objects.count(), 2)

    def test_no_duplicate_contractors_in_single_file(self):
        file_obj = build_excel_file([
            ['Ромашка', 'Комментарий 1', '+79990000001', 'info1@example.com', 'Транспорт', '', '', '', '', ''],
            ['', '', '', '', '', 'Трансфер аэропорт', 'Описание 1', '1000', '1500', 'https://example.com/1'],
            ['Ромашка', '', '', '', 'Экскурсии', '', '', '', '', ''],
            ['', '', '', '', '', 'Обзорная экскурсия', 'Описание 2', '3000', '5000', 'https://example.com/2'],
        ])

        with tenant_context(self.tenant):
            result = import_services_from_excel(file_obj)

            self.assertEqual(result['errors'], [])
            self.assertEqual(Contractor.objects.count(), 1)
            self.assertEqual(Service.objects.count(), 2)

    def test_case_insensitive_deduplication_for_categories_and_contractors(self):
        file_obj = build_excel_file([
            ['Ромашка', 'Комментарий', '+79990000001', 'info@example.com', 'Транспорт', '', '', '', '', ''],
            ['', '', '', '', '', 'Трансфер аэропорт', 'Описание 1', '1000', '1500', 'https://example.com/1'],
            ['ромашка', '', '', '', 'транспорт', '', '', '', '', ''],
            ['', '', '', '', '', 'Трансфер вокзал', 'Описание 2', '900', '1400', 'https://example.com/2'],
        ])

        with tenant_context(self.tenant):
            result = import_services_from_excel(file_obj)

            self.assertEqual(result['errors'], [])
            self.assertEqual(Contractor.objects.count(), 1)
            self.assertEqual(ServiceCategory.objects.count(), 1)
            self.assertEqual(Service.objects.count(), 2)

    def test_trim_space_deduplication_for_categories_and_contractors(self):
        file_obj = build_excel_file([
            ['  Ромашка  ', 'Комментарий', '+79990000001', 'info@example.com', '  Транспорт  ', '', '', '', '', ''],
            ['', '', '', '', '', 'Трансфер аэропорт', 'Описание 1', '1000', '1500', 'https://example.com/1'],
            ['Ромашка', '', '', '', 'Транспорт', '', '', '', '', ''],
            ['', '', '', '', '', 'Трансфер вокзал', 'Описание 2', '900', '1400', 'https://example.com/2'],
        ])

        with tenant_context(self.tenant):
            result = import_services_from_excel(file_obj)

            self.assertEqual(result['errors'], [])
            self.assertEqual(Contractor.objects.count(), 1)
            self.assertEqual(ServiceCategory.objects.count(), 1)
            self.assertEqual(Service.objects.count(), 2)

    def test_service_row_without_current_contractor_returns_error(self):
        file_obj = build_excel_file([
            ['', '', '', '', 'Транспорт', 'Трансфер аэропорт', 'Описание', '1000', '1500', 'https://example.com/1'],
        ])

        with tenant_context(self.tenant):
            result = preview_services_import(file_obj)

            self.assertEqual(result['rows_processed'], 0)
            self.assertEqual(len(result['errors']), 1)
            self.assertIn('Не заполнено поле "Подрядчик"', result['errors'][0]['message'])

    def test_service_row_without_current_category_returns_error(self):
        file_obj = build_excel_file([
            ['Ромашка', 'Комментарий', '+79990000001', 'info@example.com', '', 'Трансфер аэропорт', 'Описание', '1000', '1500', 'https://example.com/1'],
        ])

        with tenant_context(self.tenant):
            result = preview_services_import(file_obj)

            self.assertEqual(result['rows_processed'], 0)
            self.assertEqual(len(result['errors']), 1)
            self.assertIn('Не заполнено поле "Категория услуги"', result['errors'][0]['message'])

    def test_category_only_row_is_allowed_when_current_contractor_exists(self):
        file_obj = build_excel_file([
            ['Ромашка', 'Комментарий', '+79990000001', 'info@example.com', 'Транспорт', '', '', '', '', ''],
            ['', '', '', '', 'Экскурсии', '', '', '', '', ''],
            ['', '', '', '', '', 'Обзорная экскурсия', 'Описание', '3000', '5000', 'https://example.com/1'],
        ])

        with tenant_context(self.tenant):
            result = import_services_from_excel(file_obj)

            self.assertEqual(result['errors'], [])
            self.assertEqual(result['rows_processed'], 3)
            self.assertEqual(Contractor.objects.count(), 1)
            self.assertEqual(ServiceCategory.objects.count(), 1)
            self.assertEqual(Service.objects.count(), 1)

            service = Service.objects.get()
            self.assertEqual(service.category.name, 'Экскурсии')

    def test_contractor_contact_details_can_be_updated_in_context_row(self):
        with tenant_context(self.tenant):
            Contractor.objects.create(
                name='Ромашка',
                notes='Старый комментарий',
                phone='111',
                email='old@example.com',
            )

        file_obj = build_excel_file([
            ['Ромашка', 'Новый комментарий', '+79990000002', 'new@example.com', '', '', '', '', '', ''],
            ['', '', '', '', 'Транспорт', '', '', '', '', ''],
            ['', '', '', '', '', 'Трансфер аэропорт', 'Описание', '1000', '1500', 'https://example.com/1'],
        ])

        with tenant_context(self.tenant):
            result = import_services_from_excel(file_obj)

            self.assertEqual(result['errors'], [])

            contractor = Contractor.objects.get(name='Ромашка')
            self.assertEqual(contractor.notes, 'Новый комментарий')
            self.assertEqual(contractor.phone, '+79990000002')
            self.assertEqual(contractor.email, 'new@example.com')

    def test_preview_rows_are_built_for_service_rows_only(self):
        file_obj = build_excel_file([
            ['Ромашка', 'Комментарий', '+79990000001', 'info@example.com', 'Транспорт', '', '', '', '', ''],
            ['', '', '', '', '', 'Трансфер аэропорт', 'Описание 1', '1000', '1500', 'https://example.com/1'],
            ['', '', '', '', 'Экскурсии', '', '', '', '', ''],
            ['', '', '', '', '', 'Обзорная экскурсия', 'Описание 2', '3000', '5000', 'https://example.com/2'],
        ])

        with tenant_context(self.tenant):
            result = preview_services_import(file_obj)

            self.assertEqual(result['errors'], [])
            self.assertEqual(len(result['preview_rows']), 2)

            first = result['preview_rows'][0]
            second = result['preview_rows'][1]

            self.assertEqual(first['service_name'], 'Трансфер аэропорт')
            self.assertEqual(first['contractor_name'], 'Ромашка')
            self.assertEqual(first['category_name'], 'Транспорт')

            self.assertEqual(second['service_name'], 'Обзорная экскурсия')
            self.assertEqual(second['contractor_name'], 'Ромашка')
            self.assertEqual(second['category_name'], 'Экскурсии')