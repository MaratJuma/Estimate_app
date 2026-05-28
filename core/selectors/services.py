from core.models import Service, ServiceCategory, Contractor


def get_service_categories():
    return ServiceCategory.objects.order_by('sort_order', 'name')


def get_service_category_by_id(category_id):
    if not category_id:
        return None
    return ServiceCategory.objects.filter(id=category_id).first()


def get_contractor_by_id(contractor_id):
    if not contractor_id:
        return None
    return Contractor.objects.filter(id=contractor_id).first()


def get_service_list_queryset(query='', category_id=''):
    services = Service.objects.select_related('contractor', 'category').order_by('-id')

    if query:
        services = services.filter(name__icontains=query)

    if category_id:
        services = services.filter(category_id=category_id)

    return services


def get_active_services_for_estimate_item_queryset(query='', category_id='', contractor_id=''):
    services = Service.objects.select_related('contractor', 'category').filter(is_active=True)

    if query:
        services = services.filter(name__icontains=query)

    if category_id:
        services = services.filter(category_id=category_id)

    if contractor_id:
        services = services.filter(contractor_id=contractor_id)

    return services.order_by('name', 'id')


def get_contractors_for_estimate_item_filter(query='', category_id=''):
    base_services = Service.objects.filter(is_active=True)

    if query:
        base_services = base_services.filter(name__icontains=query)

    if category_id:
        base_services = base_services.filter(category_id=category_id)

    contractor_ids = base_services.values_list('contractor_id', flat=True).distinct()

    return Contractor.objects.filter(id__in=contractor_ids).order_by('name')


def get_contractors_for_service_create(query=''):
    contractors = Contractor.objects.all().order_by('name')

    if query:
        contractors = contractors.filter(name__icontains=query)

    return contractors