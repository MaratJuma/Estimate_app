from decimal import Decimal
from django.db.models import Q
from core.models import Estimate


def get_estimate_list_queryset(query=''):
    estimates = (
        Estimate.objects.all()
        .prefetch_related('days__items__service')
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
    return Estimate.objects.prefetch_related('days__items__service__contractor')


def calculate_estimate_totals(estimate):
    total_cost = Decimal('0.00')
    total_client = Decimal('0.00')

    for day in estimate.days.all():
        for item in day.items.all():
            total_cost += item.total_cost
            total_client += item.total_client

    margin = total_client - total_cost
    margin_percent = Decimal('0.00')

    if total_client != 0:
        margin_percent = (margin / total_client) * Decimal('100')

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
    return estimate


def attach_estimate_detail_day_summary(days):
    total_cost = Decimal('0.00')
    total_client = Decimal('0.00')

    for day in days:
        day_cost = Decimal('0.00')
        day_client = Decimal('0.00')

        for item in day.items.all():
            item.display_cost_price = item.cost_price
            item.display_total_cost = item.total_cost
            item.display_client_price = item.client_price
            item.display_total_client = item.total_client

            day_cost += item.display_total_cost
            day_client += item.display_total_client

        day.total_cost_sum = day_cost
        day.total_client_sum = day_client

        total_cost += day_cost
        total_client += day_client

    margin = total_client - total_cost
    margin_percent = Decimal('0.00')

    if total_client != 0:
        margin_percent = (margin / total_client) * Decimal('100')

    return {
        'days': days,
        'total_cost': total_cost,
        'total_client': total_client,
        'margin': margin,
        'margin_percent': margin_percent,
    }