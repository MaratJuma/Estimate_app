from django.db.models import Count
from core.models import ServiceCategory


def get_admin_category_list_queryset():
    return (
        ServiceCategory.objects
        .annotate(services_count=Count('services'))
        .order_by('sort_order', 'name')
    )


def get_service_category_with_usage(category_id):
    return (
        ServiceCategory.objects
        .annotate(services_count=Count('services'))
        .filter(id=category_id)
        .first()
    )