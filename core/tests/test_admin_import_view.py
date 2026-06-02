

from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django_tenants.utils import tenant_context
from openpyxl import Workbook

from core.models import Contractor, Service, ServiceCategory
from core.services.imports import EXPECTED_HEADERS
from core.tests.base import TenantTestCase
from unittest import skip


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

# @skip("Admin import page route currently returns 404; needs URL/view audit")
class AdminImportViewTests(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.admin_user = self.create_tenant_superuser(
            username='admin',
            password='pass12345',
        )
        self.sales_user = self.create_tenant_user(
            username='sales',
            password='pass12345',
        )

    def test_admin_can_open_import_page(self):
        self.tenant_login(username='admin', password='pass12345')

        response = self.tenant_get(reverse('admin_import_database'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Импорт Excel')

    def test_non_admin_cannot_open_import_page(self):
        self.tenant_login(username='sales', password='pass12345')

        response = self.tenant_get(reverse('admin_import_database'))

        self.assertEqual(response.status_code, 302)

    def test_dry_run_does_not_create_data(self):
        self.tenant_login(username='admin', password='pass12345')

        upload = build_uploaded_xlsx(rows=[
            EXPECTED_HEADERS,
            [
                'Ромашка',
                'Комментарий подрядчика',
                '',
                '',
                'Транспорт',
                'Трансфер',
                'Комментарий',
                '1000',
                '1500',
                '',
            ],
        ])

        response = self.tenant_post(
            reverse('admin_import_database'),
            data={
                'file': upload,
                'dry_run': 'on',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dry-run / только проверка')

        with tenant_context(self.tenant):
            self.assertEqual(ServiceCategory.objects.count(), 0)
            self.assertEqual(Contractor.objects.count(), 0)
            self.assertEqual(Service.objects.count(), 0)

    def test_real_import_creates_data(self):
        self.tenant_login(username='admin', password='pass12345')

        upload = build_uploaded_xlsx(rows=[
            EXPECTED_HEADERS,
            [
                'Ромашка',
                'Комментарий подрядчика',
                '',
                '',
                'Транспорт',
                'Трансфер',
                'Комментарий',
                '1000',
                '1500',
                '',
            ],
        ])

        response = self.tenant_post(
            reverse('admin_import_database'),
            data={
                'file': upload,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Импорт в базу')

        with tenant_context(self.tenant):
            self.assertEqual(ServiceCategory.objects.count(), 1)
            self.assertEqual(Contractor.objects.count(), 1)
            self.assertEqual(Service.objects.count(), 1)

    def test_invalid_extension_is_rejected(self):
        self.tenant_login(username='admin', password='pass12345')

        upload = SimpleUploadedFile(
            'import.txt',
            b'not excel',
            content_type='text/plain',
        )

        response = self.tenant_post(
            reverse('admin_import_database'),
            data={
                'file': upload,
                'dry_run': 'on',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Поддерживаются только файлы формата .xlsx')

    def test_real_import_does_not_duplicate_category_and_contractor(self):
        self.tenant_login(username='admin', password='pass12345')

        upload = build_uploaded_xlsx(rows=[
            EXPECTED_HEADERS,
            [
                'Ромашка',
                'Комментарий подрядчика',
                '',
                '',
                'Транспорт',
                'Трансфер',
                'Комментарий',
                '1000',
                '1500',
                '',
            ],
            [
                'Ромашка',
                'Комментарий подрядчика',
                '',
                '',
                'Транспорт',
                'Трансфер',
                'Комментарий',
                '1000',
                '1500',
                '',
            ],
        ])

        response = self.tenant_post(
            reverse('admin_import_database'),
            data={
                'file': upload,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        with tenant_context(self.tenant):
            self.assertEqual(ServiceCategory.objects.count(), 1)
            self.assertEqual(Contractor.objects.count(), 1)
            self.assertEqual(Service.objects.count(), 1)