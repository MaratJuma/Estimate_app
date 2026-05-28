from core.models import EstimateItem


def calculate_item_totals(qty, cost_price, client_price):
    return {
        'total_cost': qty * cost_price,
        'total_client': qty * client_price,
    }


def create_estimate_item_from_service(day, service, qty):
    totals = calculate_item_totals(
        qty=qty,
        cost_price=service.cost_price,
        client_price=service.client_price,
    )

    return EstimateItem.objects.create(
        estimate_day=day,
        service=service,
        qty=qty,
        cost_price=service.cost_price,
        client_price=service.client_price,
        total_cost=totals['total_cost'],
        total_client=totals['total_client'],
    )


def update_estimate_item(item, qty, client_price):
    item.qty = qty
    item.client_price = client_price

    # Себестоимость в позиции всегда берётся из текущей услуги
    item.cost_price = item.service.cost_price

    totals = calculate_item_totals(
        qty=item.qty,
        cost_price=item.cost_price,
        client_price=item.client_price,
    )

    item.total_cost = totals['total_cost']
    item.total_client = totals['total_client']
    item.save()

    return item


def sync_draft_estimate_items_cost(service):
    items = list(
        EstimateItem.objects.filter(
            service=service,
            estimate_day__estimate__is_approved=False
        )
    )

    for item in items:
        item.cost_price = service.cost_price
        item.total_cost = item.qty * service.cost_price

    EstimateItem.objects.bulk_update(items, ['cost_price', 'total_cost'])

    return len(items)