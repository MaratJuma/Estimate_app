from django.db.models import Count
from core.models import Contractor, ServiceCategory


def get_contractor_list_queryset(query='', category_id=''):
    contractors = (
        Contractor.objects
        .annotate(services_count=Count('services', distinct=True))
        .order_by('-id')
    )

    if query:
        contractors = contractors.filter(name__icontains=query)

    if category_id:
        contractors = contractors.filter(services__category_id=category_id).distinct()

    return contractors


def get_contractor_category_by_id(category_id):
    if not category_id:
        return None
    return ServiceCategory.objects.filter(id=category_id).first()