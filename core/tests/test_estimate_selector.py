from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Contractor, ServiceCategory, Service, EstimateItem
from core.selectors.estimates import (
    calculate_estimate_totals,
    calculate_margin_percent,
    attach_estimate_detail_day_summary,
    get_estimate_detail_queryset,
)
from core.services.estimates import create_estimate_with_first_day

User = get_user_model()


class EstimateSelectorsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='manager',
            password='pass12345',
        )
        self.category = ServiceCategory.objects.create(name='Транспорт', sort_order=1)
        self.contractor = Contractor.objects.create(name='Поставщик')
        self.service = Service.objects.create(
            contractor=self.contractor,
            category=self.category,
            name='Трансфер',
            description='',
            cost_price=Decimal('100.00'),
            client_price=Decimal('150.00'),
            is_active=True,
            image_url='',
        )

    def test_calculate_margin_percent(self):
        result = calculate_margin_percent(
            Decimal('200.00'),
            Decimal('500.00'),
        )
        self.assertEqual(result, Decimal('60.00'))

    def test_calculate_margin_percent_returns_zero_when_total_client_zero(self):
        result = calculate_margin_percent(
            Decimal('200.00'),
            Decimal('0.00'),
        )
        self.assertEqual(result, Decimal('0.00'))

    def test_calculate_estimate_totals(self):
        estimate = create_estimate_with_first_day(
            client_name='Клиент',
            comment='',
            user=self.user,
        )
        day = estimate.days.first()

        EstimateItem.objects.create(
            estimate_day=day,
            service=self.service,
            qty=Decimal('2.00'),
            cost_price=Decimal('100.00'),
            client_price=Decimal('150.00'),
            total_cost=Decimal('200.00'),
            total_client=Decimal('300.00'),
        )

        estimate = get_estimate_detail_queryset().get(id=estimate.id)
        totals = calculate_estimate_totals(estimate)

        self.assertEqual(totals['total_cost'], Decimal('200.00'))
        self.assertEqual(totals['total_client'], Decimal('300.00'))
        self.assertEqual(totals['margin'], Decimal('100.00'))
        self.assertEqual(
            totals['margin_percent'],
            Decimal('33.33333333333333333333333333')
        )

    def test_attach_estimate_detail_day_summary(self):
        estimate = create_estimate_with_first_day(
            client_name='Клиент',
            comment='',
            user=self.user,
        )
        day = estimate.days.first()

        EstimateItem.objects.create(
            estimate_day=day,
            service=self.service,
            qty=Decimal('2.00'),
            cost_price=Decimal('100.00'),
            client_price=Decimal('150.00'),
            total_cost=Decimal('200.00'),
            total_client=Decimal('300.00'),
        )

        estimate = get_estimate_detail_queryset().get(id=estimate.id)
        days = list(estimate.days.all())

        result = attach_estimate_detail_day_summary(days)

        self.assertEqual(result['total_cost'], Decimal('200.00'))
        self.assertEqual(result['total_client'], Decimal('300.00'))
        self.assertEqual(result['margin'], Decimal('100.00'))

        day = result['days'][0]
        self.assertEqual(day.total_cost_sum, Decimal('200.00'))
        self.assertEqual(day.total_client_sum, Decimal('300.00'))

        item = list(day.items.all())[0]

        self.assertEqual(item.display_cost_price, Decimal('100.00'))
        self.assertEqual(item.display_client_price, Decimal('150.00'))
        self.assertEqual(item.display_total_cost, Decimal('200.00'))
        self.assertEqual(item.display_total_client, Decimal('300.00'))