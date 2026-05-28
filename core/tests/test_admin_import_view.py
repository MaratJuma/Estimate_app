from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from openpyxl import Workbook

from core.models import Contractor, Service, ServiceCategory
from core.services.imports import EXPECTED_HEADERS

User = get_user_model()


def build_uploaded_xlsx(filename='import.xlsx', rows=None):
    wb = Workbook()
    ws = wb.active

    for row in rows or []:
        ws.append(row)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return SimpleUploadedFile(
        filename,
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


class AdminImportViewTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='pass12345',
            is_superuser=True,
            is_staff=True,
        )
        self.sales_user = User.objects.create_user(
            username='sales',
            password='pass12345',
        )

    def test_admin_can_open_import_page(self):
        self.client.login(username='admin', password='pass12345')

        response = self.client.get(reverse('admin_import_database'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Импорт Excel')

    def test_non_admin_cannot_open_import_page(self):
        self.client.login(username='sales', password='pass12345')

        response = self.client.get(reverse('admin_import_database'))

        self.assertEqual(response.status_code, 302)

    def test_dry_run_does_not_create_data(self):
        self.client.login(username='admin', password='pass12345')

        upload = build_uploaded_xlsx(rows=[
            EXPECTED_HEADERS,
            [
                'Транспорт',
                'Трансфер',
                'Комментарий',
                'Ромашка',
                'Комментарий подрядчика',
                '1000',
                '1500',
                '',
                '',
                '',
            ],
        ])

        response = self.client.post(
            reverse('admin_import_database'),
            data={
                'file': upload,
                'dry_run': 'on',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dry-run / только проверка')
        self.assertEqual(ServiceCategory.objects.count(), 0)
        self.assertEqual(Contractor.objects.count(), 0)
        self.assertEqual(Service.objects.count(), 0)

    def test_real_import_creates_data(self):
        self.client.login(username='admin', password='pass12345')

        upload = build_uploaded_xlsx(rows=[
            EXPECTED_HEADERS,
            [
                'Транспорт',
                'Трансфер',
                'Комментарий',
                'Ромашка',
                'Комментарий подрядчика',
                '1000',
                '1500',
                '',
                '',
                '',
            ],
        ])

        response = self.client.post(
            reverse('admin_import_database'),
            data={
                'file': upload,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Импорт в базу')
        self.assertEqual(ServiceCategory.objects.count(), 1)
        self.assertEqual(Contractor.objects.count(), 1)
        self.assertEqual(Service.objects.count(), 1)

    def test_invalid_extension_is_rejected(self):
        self.client.login(username='admin', password='pass12345')

        upload = SimpleUploadedFile(
            'import.txt',
            b'not excel',
            content_type='text/plain',
        )

        response = self.client.post(
            reverse('admin_import_database'),
            data={
                'file': upload,
                'dry_run': 'on',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Поддерживаются только файлы формата .xlsx')


def test_real_import_does_not_duplicate_category_and_contractor(self):
        self.client.login(username='admin', password='pass12345')

        upload = build_uploaded_xlsx(rows=[
            EXPECTED_HEADERS,
            [
                'Транспорт',
                'Трансфер аэропорт',
                'Комментарий 1',
                'Ромашка',
                'Комментарий подрядчика 1',
                '1000',
                '1500',
                '',
                '',
                '',
            ],
            [
                'Транспорт',
                'Трансфер вокзал',
                'Комментарий 2',
                'Ромашка',
                'Комментарий подрядчика 2',
                '1200',
                '1800',
                '',
                '',
                '',
            ],
        ])

        response = self.client.post(
            reverse('admin_import_database'),
            data={
                'file': upload,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ServiceCategory.objects.count(), 1)
        self.assertEqual(Contractor.objects.count(), 1)
        self.assertEqual(Service.objects.count(), 2)

