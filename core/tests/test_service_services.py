from decimal import Decimal
from django.test import TestCase
from core.models import (
    Contractor,
    ServiceCategory,
    Service,
    Estimate,
    EstimateDay,
    EstimateItem,
)
from core.services.services import handle_service_cost_change


class ServiceBusinessLogicTestCase(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(
            name='Экскурсия',
            sort_order=1,
        )
        self.contractor = Contractor.objects.create(name='Поставщик')
        self.service = Service.objects.create(
            contractor=self.contractor,
            name='Услуга 1',
            category=self.category,
            description='',
            cost_price=Decimal('100.00'),
            client_price=Decimal('180.00'),
            is_active=True,
            image_url='',
        )

        self.draft_estimate = Estimate.objects.create(
            client_name='Черновик',
            manager_name='Менеджер',
            comment='',
            is_approved=False,
        )
        self.draft_day = EstimateDay.objects.create(
            estimate=self.draft_estimate,
            day_number=1,
            title='День 1',
            description='',
        )

        self.approved_estimate = Estimate.objects.create(
            client_name='Утвержденная',
            manager_name='Менеджер',
            comment='',
            is_approved=True,
        )
        self.approved_day = EstimateDay.objects.create(
            estimate=self.approved_estimate,
            day_number=1,
            title='День 1',
            description='',
        )

    def test_handle_service_cost_change_updates_only_draft_items(self):
        draft_item = EstimateItem.objects.create(
            estimate_day=self.draft_day,
            service=self.service,
            qty=Decimal('2.00'),
            cost_price=Decimal('100.00'),
            client_price=Decimal('180.00'),
            total_cost=Decimal('200.00'),
            total_client=Decimal('360.00'),
        )

        approved_item = EstimateItem.objects.create(
            estimate_day=self.approved_day,
            service=self.service,
            qty=Decimal('2.00'),
            cost_price=Decimal('100.00'),
            client_price=Decimal('180.00'),
            total_cost=Decimal('200.00'),
            total_client=Decimal('360.00'),
        )

        old_cost_price = self.service.cost_price
        self.service.cost_price = Decimal('130.00')
        self.service.save()

        updated_count = handle_service_cost_change(self.service, old_cost_price)

        draft_item.refresh_from_db()
        approved_item.refresh_from_db()

        self.assertEqual(updated_count, 1)
        self.assertEqual(draft_item.cost_price, Decimal('130.00'))
        self.assertEqual(draft_item.total_cost, Decimal('260.00'))

        self.assertEqual(approved_item.cost_price, Decimal('100.00'))
        self.assertEqual(approved_item.total_cost, Decimal('200.00'))

    def test_handle_service_cost_change_does_nothing_if_cost_not_changed(self):
        EstimateItem.objects.create(
            estimate_day=self.draft_day,
            service=self.service,
            qty=Decimal('2.00'),
            cost_price=Decimal('100.00'),
            client_price=Decimal('180.00'),
            total_cost=Decimal('200.00'),
            total_client=Decimal('360.00'),
        )

        updated_count = handle_service_cost_change(self.service, Decimal('100.00'))

        self.assertEqual(updated_count, 0)