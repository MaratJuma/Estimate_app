from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from openpyxl import Workbook

from core.models import Contractor, Service, ServiceCategory
from core.services.imports import (
    EXPECTED_HEADERS,
    import_services_from_excel,
    preview_services_import,
)


def build_xlsx(rows):
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


class ImportServicesTests(TestCase):
    def test_preview_does_not_write_to_database(self):
        file_content = build_xlsx([
            EXPECTED_HEADERS,
            [
                'Транспорт',
                'Трансфер аэропорт',
                'Комментарий по услуге',
                'Ромашка',
                'Комментарий по подрядчику',
                '1000',
                '1500',
                '+79990000000',
                'test@example.com',
                'https://example.com/image.jpg',
            ],
        ])

        result = preview_services_import(BytesIO(file_content))

        self.assertTrue(result['dry_run'])
        self.assertEqual(result['rows_processed'], 1)
        self.assertEqual(result['categories_created'], 1)
        self.assertEqual(result['contractors_created'], 1)
        self.assertEqual(result['services_created'], 1)

        self.assertEqual(ServiceCategory.objects.count(), 0)
        self.assertEqual(Contractor.objects.count(), 0)
        self.assertEqual(Service.objects.count(), 0)

    def test_import_writes_to_database(self):
        file_content = build_xlsx([
            EXPECTED_HEADERS,
            [
                'Экскурсии',
                'Обзорная экскурсия',
                'Описание',
                'ТурСервис',
                'Надёжный подрядчик',
                '2500',
                '4000',
                '+79991112233',
                'tour@example.com',
                'https://example.com/tour.jpg',
            ],
        ])

        result = import_services_from_excel(BytesIO(file_content))

        self.assertFalse(result['dry_run'])
        self.assertEqual(result['rows_processed'], 1)
        self.assertEqual(ServiceCategory.objects.count(), 1)
        self.assertEqual(Contractor.objects.count(), 1)
        self.assertEqual(Service.objects.count(), 1)

        category = ServiceCategory.objects.get()
        contractor = Contractor.objects.get()
        service = Service.objects.get()

        self.assertEqual(category.name, 'Экскурсии')
        self.assertEqual(contractor.name, 'ТурСервис')
        self.assertEqual(service.name, 'Обзорная экскурсия')
        self.assertEqual(service.cost_price, Decimal('2500'))
        self.assertEqual(service.client_price, Decimal('4000'))

    def test_import_updates_existing_service(self):
        category = ServiceCategory.objects.create(name='Экскурсии')
        contractor = Contractor.objects.create(name='ТурСервис')
        service = Service.objects.create(
            contractor=contractor,
            category=category,
            name='Обзорная экскурсия',
            description='Старое описание',
            cost_price=Decimal('1000'),
            client_price=Decimal('2000'),
            is_active=True,
            image_url='',
        )

        file_content = build_xlsx([
            EXPECTED_HEADERS,
            [
                'Экскурсии',
                'Обзорная экскурсия',
                'Новое описание',
                'ТурСервис',
                'Новый комментарий подрядчика',
                '3000',
                '4500',
                '+79990001122',
                'new@example.com',
                'https://example.com/new.jpg',
            ],
        ])

        result = import_services_from_excel(BytesIO(file_content))

        service.refresh_from_db()
        contractor.refresh_from_db()

        self.assertEqual(result['services_updated'], 1)
        self.assertEqual(service.description, 'Новое описание')
        self.assertEqual(service.cost_price, Decimal('3000'))
        self.assertEqual(service.client_price, Decimal('4500'))
        self.assertEqual(service.image_url, 'https://example.com/new.jpg')
        self.assertEqual(contractor.phone, '+79990001122')
        self.assertEqual(contractor.email, 'new@example.com')
        self.assertEqual(contractor.notes, 'Новый комментарий подрядчика')

    def test_invalid_headers_raise_error(self):
        file_content = build_xlsx([
            ['Неверный', 'Заголовок'],
        ])

        with self.assertRaises(ValueError):
            preview_services_import(BytesIO(file_content))

    def test_invalid_row_is_added_to_errors(self):
        file_content = build_xlsx([
            EXPECTED_HEADERS,
            [
                'Экскурсии',
                'Обзорная экскурсия',
                'Описание',
                'ТурСервис',
                'Комментарий',
                'не число',
                '4500',
                '',
                '',
                '',
            ],
        ])

        result = preview_services_import(BytesIO(file_content))

        self.assertEqual(result['rows_processed'], 0)
        self.assertEqual(len(result['errors']), 1)
        self.assertEqual(result['errors'][0]['row'], 2)

    def test_empty_rows_are_skipped(self):
        file_content = build_xlsx([
            EXPECTED_HEADERS,
            ['', '', '', '', '', '', '', '', '', ''],
            [
                'Экскурсии',
                'Обзорная экскурсия',
                'Описание',
                'ТурСервис',
                'Комментарий',
                '1000',
                '1500',
                '',
                '',
                '',
            ],
        ])

        result = preview_services_import(BytesIO(file_content))

        self.assertEqual(result['rows_skipped'], 1)
        self.assertEqual(result['rows_processed'], 1)


def test_import_does_not_duplicate_categories_with_same_name(self):
        file_content = build_xlsx([
            EXPECTED_HEADERS,
            [
                'Транспорт',
                'Трансфер аэропорт',
                'Описание 1',
                'Ромашка',
                'Комментарий подрядчика',
                '1000',
                '1500',
                '',
                '',
                '',
            ],
            [
                'Транспорт',
                'Трансфер вокзал',
                'Описание 2',
                'Лотос',
                'Комментарий подрядчика 2',
                '1200',
                '1700',
                '',
                '',
                '',
            ],
        ])

        result = import_services_from_excel(BytesIO(file_content))

        self.assertEqual(result['rows_processed'], 2)
        self.assertEqual(ServiceCategory.objects.count(), 1)
        self.assertEqual(Service.objects.count(), 2)
        self.assertEqual(Contractor.objects.count(), 2)

def test_import_does_not_duplicate_contractors_with_same_name(self):
        file_content = build_xlsx([
            EXPECTED_HEADERS,
            [
                'Транспорт',
                'Трансфер аэропорт',
                'Описание 1',
                'Ромашка',
                'Комментарий подрядчика',
                '1000',
                '1500',
                '111',
                'a@example.com',
                '',
            ],
            [
                'Экскурсии',
                'Обзорная экскурсия',
                'Описание 2',
                'Ромашка',
                'Новый комментарий подрядчика',
                '2000',
                '3000',
                '222',
                'b@example.com',
                '',
            ],
        ])

        result = import_services_from_excel(BytesIO(file_content))

        self.assertEqual(result['rows_processed'], 2)
        self.assertEqual(Contractor.objects.count(), 1)
        self.assertEqual(ServiceCategory.objects.count(), 2)
        self.assertEqual(Service.objects.count(), 2)

        contractor = Contractor.objects.get()
        self.assertEqual(contractor.name, 'Ромашка')

def test_import_treats_category_names_case_insensitively(self):
        file_content = build_xlsx([
            EXPECTED_HEADERS,
            [
                'Транспорт',
                'Трансфер аэропорт',
                'Описание 1',
                'Ромашка',
                '',
                '1000',
                '1500',
                '',
                '',
                '',
            ],
            [
                'транспорт',
                'Трансфер вокзал',
                'Описание 2',
                'Лотос',
                '',
                '1200',
                '1800',
                '',
                '',
                '',
            ],
        ])

        result = import_services_from_excel(BytesIO(file_content))

        self.assertEqual(result['rows_processed'], 2)
        self.assertEqual(ServiceCategory.objects.count(), 1)
        self.assertEqual(Service.objects.count(), 2)

def test_import_treats_contractor_names_case_insensitively(self):
        file_content = build_xlsx([
            EXPECTED_HEADERS,
            [
                'Транспорт',
                'Трансфер аэропорт',
                'Описание 1',
                'Ромашка',
                '',
                '1000',
                '1500',
                '',
                '',
                '',
            ],
            [
                'Экскурсии',
                'Обзорная экскурсия',
                'Описание 2',
                'ромашка',
                '',
                '1200',
                '1800',
                '',
                '',
                '',
            ],
        ])

        result = import_services_from_excel(BytesIO(file_content))

        self.assertEqual(result['rows_processed'], 2)
        self.assertEqual(Contractor.objects.count(), 1)
        self.assertEqual(Service.objects.count(), 2)

def test_import_strips_spaces_and_does_not_duplicate_category_or_contractor(self):
        file_content = build_xlsx([
            EXPECTED_HEADERS,
            [
                ' Транспорт ',
                'Трансфер аэропорт',
                'Описание 1',
                ' Ромашка ',
                '',
                '1000',
                '1500',
                '',
                '',
                '',
            ],
            [
                'Транспорт',
                'Трансфер вокзал',
                'Описание 2',
                'Ромашка',
                '',
                '1200',
                '1800',
                '',
                '',
                '',
            ],
        ])

        result = import_services_from_excel(BytesIO(file_content))

        self.assertEqual(result['rows_processed'], 2)
        self.assertEqual(ServiceCategory.objects.count(), 1)
        self.assertEqual(Contractor.objects.count(), 1)
        self.assertEqual(Service.objects.count(), 2)

def test_import_allows_many_services_for_same_category_and_same_contractor(self):
        file_content = build_xlsx([
            EXPECTED_HEADERS,
            [
                'Транспорт',
                'Трансфер аэропорт',
                'Описание 1',
                'Ромашка',
                '',
                '1000',
                '1500',
                '',
                '',
                '',
            ],
            [
                'Транспорт',
                'Трансфер вокзал',
                'Описание 2',
                'Ромашка',
                '',
                '1300',
                '1900',
                '',
                '',
                '',
            ],
        ])

        result = import_services_from_excel(BytesIO(file_content))

        self.assertEqual(result['rows_processed'], 2)
        self.assertEqual(ServiceCategory.objects.count(), 1)
        self.assertEqual(Contractor.objects.count(), 1)
        self.assertEqual(Service.objects.count(), 2)

        contractor = Contractor.objects.get()
        category = ServiceCategory.objects.get()

        self.assertEqual(contractor.services.count(), 2)
        self.assertEqual(category.services.count(), 2)    


def test_preview_does_not_duplicate_categories_or_contractors(self):
        file_content = build_xlsx([
            EXPECTED_HEADERS,
            [
                'Транспорт',
                'Трансфер аэропорт',
                'Описание 1',
                'Ромашка',
                '',
                '1000',
                '1500',
                '',
                '',
                '',
            ],
            [
                'Транспорт',
                'Трансфер вокзал',
                'Описание 2',
                'Ромашка',
                '',
                '1200',
                '1700',
                '',
                '',
                '',
            ],
        ])

        result = preview_services_import(BytesIO(file_content))

        self.assertTrue(result['dry_run'])
        self.assertEqual(result['rows_processed'], 2)
        self.assertEqual(result['categories_created'], 1)
        self.assertEqual(result['categories_found'], 1)
        self.assertEqual(result['contractors_created'], 1)
        self.assertEqual(result['contractors_found'], 1)
        self.assertEqual(result['services_created'], 2)

        self.assertEqual(ServiceCategory.objects.count(), 0)
        self.assertEqual(Contractor.objects.count(), 0)
        self.assertEqual(Service.objects.count(), 0)


