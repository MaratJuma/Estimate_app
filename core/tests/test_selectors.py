from decimal import Decimal

from django_tenants.utils import tenant_context

from core.models import Contractor, ServiceCategory, Service, Estimate, EstimateDay, EstimateItem
from core.selectors.services import (
    get_service_list_queryset,
    get_active_services_for_estimate_item_queryset,
    get_contractors_for_estimate_item_filter,
)
from core.selectors.contractors import get_contractor_list_queryset
from core.selectors.estimates import get_estimate_list_queryset, calculate_estimate_totals
from core.tests.base import TenantTestCase


class SelectorsTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()

        with tenant_context(self.tenant):
            self.category1 = ServiceCategory.objects.create(name='Трансфер', sort_order=1)
            self.category2 = ServiceCategory.objects.create(name='Экскурсия', sort_order=2)

            self.contractor1 = Contractor.objects.create(name='Альфа')
            self.contractor2 = Contractor.objects.create(name='Бета')

            self.service1 = Service.objects.create(
                contractor=self.contractor1,
                name='Трансфер аэропорт',
                category=self.category1,
                cost_price=Decimal('100.00'),
                client_price=Decimal('150.00'),
                is_active=True,
            )
            self.service2 = Service.objects.create(
                contractor=self.contractor2,
                name='Экскурсия на маяк',
                category=self.category2,
                cost_price=Decimal('200.00'),
                client_price=Decimal('300.00'),
                is_active=True,
            )
            self.service3 = Service.objects.create(
                contractor=self.contractor1,
                name='Старый трансфер',
                category=self.category1,
                cost_price=Decimal('90.00'),
                client_price=Decimal('120.00'),
                is_active=False,
            )

    def test_get_service_list_queryset_filters_by_query(self):
        with tenant_context(self.tenant):
            qs = get_service_list_queryset(query='аэропорт')
            self.assertEqual(qs.count(), 1)
            self.assertEqual(qs.first(), self.service1)

    def test_get_service_list_queryset_filters_by_category(self):
        with tenant_context(self.tenant):
            qs = get_service_list_queryset(category_id=str(self.category2.id))
            self.assertEqual(qs.count(), 1)
            self.assertEqual(qs.first(), self.service2)

    def test_get_active_services_for_estimate_item_queryset_excludes_inactive(self):
        with tenant_context(self.tenant):
            qs = get_active_services_for_estimate_item_queryset(category_id=str(self.category1.id))
            self.assertEqual(qs.count(), 1)
            self.assertEqual(qs.first(), self.service1)

    def test_get_contractors_for_estimate_item_filter_returns_only_relevant_contractors(self):
        with tenant_context(self.tenant):
            qs = get_contractors_for_estimate_item_filter(category_id=str(self.category2.id))
            self.assertEqual(list(qs), [self.contractor2])

    def test_get_contractor_list_queryset_filters_by_service_category(self):
        with tenant_context(self.tenant):
            qs = get_contractor_list_queryset(category_id=str(self.category1.id))
            self.assertEqual(list(qs), [self.contractor1])

    def test_get_estimate_list_queryset_filters_by_text(self):
        estimate1 = Estimate.objects.create(
            client_name='ООО Альфа',
            manager_name='Иван',
            comment='Важный клиент',
            contract_number='DOG-ALPHA-001',
            contract_estimate_number=1,
        )

        Estimate.objects.create(
            client_name='ООО Бета',
            manager_name='Петр',
            comment='Обычный клиент',
            contract_number='DOG-BETA-001',
            contract_estimate_number=1,
        )

        result = get_estimate_list_queryset(query='Альфа')

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().id, estimate1.id)

    def test_calculate_estimate_totals_returns_correct_numbers(self):
        with tenant_context(self.tenant):
            estimate = Estimate.objects.create(
                client_name='Клиент',
                manager_name='Менеджер',
                contract_number='DOG-SELECTOR-001',
                contract_estimate_number=1,
            )
            day = EstimateDay.objects.create(
                estimate=estimate,
                day_number=1,
                title='День 1',
                description='',
            )

            EstimateItem.objects.create(
                estimate_day=day,
                service=self.service1,
                qty=Decimal('2.00'),
                cost_price=Decimal('100.00'),
                client_price=Decimal('150.00'),
                total_cost=Decimal('200.00'),
                total_client=Decimal('300.00'),
            )

            totals = calculate_estimate_totals(estimate)

        self.assertEqual(totals['total_cost'], Decimal('200.00'))
        self.assertEqual(totals['total_client'], Decimal('300.00'))
        self.assertEqual(totals['margin'], Decimal('100.00'))