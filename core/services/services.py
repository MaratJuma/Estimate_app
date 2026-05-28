from core.services.estimate_items import sync_draft_estimate_items_cost


def handle_service_cost_change(service, old_cost_price):
    if service.cost_price != old_cost_price:
        return sync_draft_estimate_items_cost(service)
    return 0