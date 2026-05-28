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
from core.services.estimates import (
    create_estimate_with_first_day,
    approve_estimate,
    duplicate_estimate,
)
from core.services.estimate_days import (
    create_next_estimate_day,
    delete_day_and_renumber,
)
from core.services.estimate_items import (
    create_estimate_item_from_service,
    update_estimate_item,
)


class EstimateServicesTestCase(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(
            name='Трансфер',
            sort_order=1,
        )
        self.contractor = Contractor.objects.create(
            name='Тестовый поставщик',
            contact_name='Иван',
            phone='123',
            email='test@example.com',
            notes='Комментарий',
        )
        self.service = Service.objects.create(
            contractor=self.contractor,
            name='Трансфер аэропорт',
            category=self.category,
            description='Описание',
            cost_price=Decimal('100.00'),
            client_price=Decimal('150.00'),
            is_active=True,
            image_url='https://example.com/image.jpg',
        )

    def test_create_estimate_with_first_day_creates_day_one(self):
        estimate = create_estimate_with_first_day(
            client_name='ООО Ромашка',
            manager_name='Менеджер 1',
            comment='Тестовая смета',
        )

        self.assertEqual(Estimate.objects.count(), 1)
        self.assertEqual(EstimateDay.objects.count(), 1)

        day = estimate.days.first()
        self.assertIsNotNone(day)
        self.assertEqual(day.day_number, 1)

    def test_create_next_estimate_day_uses_next_number(self):
        estimate = create_estimate_with_first_day(
            client_name='Клиент',
            manager_name='Менеджер',
            comment='',
        )

        day2 = create_next_estimate_day(
            estimate=estimate,
            title='Второй день',
            description='Описание второго дня',
        )

        self.assertEqual(day2.day_number, 2)
        self.assertEqual(day2.title, 'Второй день')
        self.assertEqual(estimate.days.count(), 2)

    def test_delete_day_and_renumber_shifts_following_days(self):
        estimate = create_estimate_with_first_day(
            client_name='Клиент',
            manager_name='Менеджер',
            comment='',
        )

        day2 = create_next_estimate_day(estimate, title='День 2', description='')
        day3 = create_next_estimate_day(estimate, title='День 3', description='')

        deleted_number = delete_day_and_renumber(day2)

        self.assertEqual(deleted_number, 2)
        self.assertFalse(EstimateDay.objects.filter(id=day2.id).exists())

        day3.refresh_from_db()
        self.assertEqual(day3.day_number, 2)

    def test_create_estimate_item_from_service_copies_prices_and_totals(self):
        estimate = create_estimate_with_first_day(
            client_name='Клиент',
            manager_name='Менеджер',
            comment='',
        )
        day = estimate.days.first()

        item = create_estimate_item_from_service(
            day=day,
            service=self.service,
            qty=Decimal('2.00'),
        )

        self.assertEqual(item.cost_price, Decimal('100.00'))
        self.assertEqual(item.client_price, Decimal('150.00'))
        self.assertEqual(item.total_cost, Decimal('200.00'))
        self.assertEqual(item.total_client, Decimal('300.00'))

    def test_update_estimate_item_recalculates_totals(self):
        estimate = create_estimate_with_first_day(
            client_name='Клиент',
            manager_name='Менеджер',
            comment='',
        )
        day = estimate.days.first()

        item = create_estimate_item_from_service(
            day=day,
            service=self.service,
            qty=Decimal('2.00'),
        )

        updated_item = update_estimate_item(
            item=item,
            qty=Decimal('3.00'),
            client_price=Decimal('170.00'),
        )

        self.assertEqual(updated_item.qty, Decimal('3.00'))
        self.assertEqual(updated_item.cost_price, Decimal('100.00'))
        self.assertEqual(updated_item.client_price, Decimal('170.00'))
        self.assertEqual(updated_item.total_cost, Decimal('300.00'))
        self.assertEqual(updated_item.total_client, Decimal('510.00'))

    def test_approve_estimate_updates_item_costs_and_sets_approved_fields(self):
        estimate = create_estimate_with_first_day(
            client_name='Клиент',
            manager_name='Менеджер',
            comment='',
        )
        day = estimate.days.first()

        item = EstimateItem.objects.create(
            estimate_day=day,
            service=self.service,
            qty=Decimal('2.00'),
            cost_price=Decimal('90.00'),
            client_price=Decimal('150.00'),
            total_cost=Decimal('180.00'),
            total_client=Decimal('300.00'),
        )

        approve_estimate(estimate)

        estimate.refresh_from_db()
        item.refresh_from_db()

        self.assertTrue(estimate.is_approved)
        self.assertIsNotNone(estimate.approved_at)
        self.assertEqual(item.cost_price, Decimal('100.00'))
        self.assertEqual(item.total_cost, Decimal('200.00'))
        self.assertEqual(item.total_client, Decimal('300.00'))

    def test_duplicate_estimate_creates_copy_with_actual_cost_prices(self):
        source_estimate = create_estimate_with_first_day(
            client_name='Клиент',
            manager_name='Менеджер',
            comment='Исходная смета',
        )
        source_day = source_estimate.days.first()

        EstimateItem.objects.create(
            estimate_day=source_day,
            service=self.service,
            qty=Decimal('2.00'),
            cost_price=Decimal('80.00'),
            client_price=Decimal('150.00'),
            total_cost=Decimal('160.00'),
            total_client=Decimal('300.00'),
        )

        self.service.cost_price = Decimal('120.00')
        self.service.save()

        new_estimate = duplicate_estimate(source_estimate)

        self.assertNotEqual(new_estimate.id, source_estimate.id)
        self.assertEqual(new_estimate.client_name, source_estimate.client_name)
        self.assertFalse(new_estimate.is_approved)
        self.assertIn(f'копия сметы #{source_estimate.id}', new_estimate.comment.lower())

        new_day = new_estimate.days.first()
        new_item = new_day.items.first()

        self.assertEqual(new_item.cost_price, Decimal('120.00'))
        self.assertEqual(new_item.client_price, Decimal('150.00'))
        self.assertEqual(new_item.total_cost, Decimal('240.00'))
        self.assertEqual(new_item.total_client, Decimal('300.00'))