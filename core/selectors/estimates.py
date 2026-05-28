from decimal import Decimal

from django.db.models import Prefetch, Q

from core.models import Estimate, EstimateDay, EstimateItem


def get_estimate_list_queryset(query=''):
    item_qs = (
        EstimateItem.objects
        .select_related('service', 'service__contractor', 'service__category')
        .order_by('id')
    )

    day_qs = (
        EstimateDay.objects
        .prefetch_related(
            Prefetch('items', queryset=item_qs)
        )
        .order_by('day_number', 'id')
    )

    estimates = (
        Estimate.objects.all()
        .select_related('created_by')
        .prefetch_related(
            Prefetch('days', queryset=day_qs)
        )
        .order_by('-created_at')
    )

    if query:
        estimates = estimates.filter(
            Q(client_name__icontains=query) |
            Q(manager_name__icontains=query) |
            Q(comment__icontains=query)
        )

    return estimates


def get_estimate_detail_queryset():
    item_qs = (
        EstimateItem.objects
        .select_related('service', 'service__contractor', 'service__category')
        .order_by('id')
    )

    day_qs = (
        EstimateDay.objects
        .prefetch_related(
            Prefetch('items', queryset=item_qs)
        )
        .order_by('day_number', 'id')
    )

    return (
        Estimate.objects
        .select_related('created_by')
        .prefetch_related(
            Prefetch('days', queryset=day_qs)
        )
    )


def calculate_margin_percent(total_cost, total_client):
    if total_client == 0:
        return Decimal('0.00')

    margin = total_client - total_cost
    return (margin / total_client) * Decimal('100')


def calculate_estimate_totals(estimate):
    total_cost = Decimal('0.00')
    total_client = Decimal('0.00')

    for day in estimate.days.all():
        for item in day.items.all():
            item_cost = item.total_cost or Decimal('0.00')
            item_client = item.total_client or Decimal('0.00')

            total_cost += item_cost
            total_client += item_client

    margin = total_client - total_cost
    margin_percent = calculate_margin_percent(total_cost, total_client)

    return {
        'total_cost': total_cost,
        'total_client': total_client,
        'margin': margin,
        'margin_percent': margin_percent,
    }


def attach_estimate_list_summary(estimate):
    totals = calculate_estimate_totals(estimate)

    estimate.days_count_value = estimate.days.count()
    estimate.total_cost_sum = totals['total_cost']
    estimate.total_client_sum = totals['total_client']
    estimate.margin_sum = totals['margin']
    estimate.margin_percent_sum = totals['margin_percent']

    return estimate


def attach_estimate_detail_day_summary(days):
    total_cost = Decimal('0.00')
    total_client = Decimal('0.00')

    for day in days:
        day_cost = Decimal('0.00')
        day_client = Decimal('0.00')

        for item in day.items.all():
            item.display_cost_price = item.cost_price or Decimal('0.00')
            item.display_total_cost = item.total_cost or Decimal('0.00')
            item.display_client_price = item.client_price or Decimal('0.00')
            item.display_total_client = item.total_client or Decimal('0.00')

            day_cost += item.display_total_cost
            day_client += item.display_total_client

        day.total_cost_sum = day_cost
        day.total_client_sum = day_client

        total_cost += day_cost
        total_client += day_client

    margin = total_client - total_cost
    margin_percent = calculate_margin_percent(total_cost, total_client)

    return {
        'days': days,
        'total_cost': total_cost,
        'total_client': total_client,
        'margin': margin,
        'margin_percent': margin_percent,
    }