from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from ..forms import (
    ServiceCreateForm,
    ServiceForContractorCreateForm,
    ServiceUpdateForm,
)
from ..models import Contractor, EstimateItem, Service
from ..permissions import (
    can_manage_services,
    deny_access,
    is_sales_manager,
)
from ..selectors.services import (
    get_contractor_by_id,
    get_contractors_for_service_create,
    get_service_categories,
    get_service_category_by_id,
    get_service_list_queryset,
)
from ..services.services import handle_service_cost_change
from ..utils import build_pagination_slots, build_query_params_without_page, get_next_url

@login_required
def service_list(request):
    query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()

    services = get_service_list_queryset(
        query=query,
        category_id=selected_category,
    )

    categories = get_service_categories()
    selected_category_obj = get_service_category_by_id(selected_category)

    paginator = Paginator(services, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    pagination_slots = build_pagination_slots(page_obj)

    return render(request, 'core/service_list.html', {
        'services': page_obj,
        'page_obj': page_obj,
        'pagination_slots': pagination_slots,
        'query': query,
        'categories': categories,
        'selected_category': selected_category,
        'selected_category_obj': selected_category_obj,
        'selected_category_name': selected_category_obj.name if selected_category_obj else '',
        'query_params': build_query_params_without_page(request),
        'current_full_path': request.get_full_path(),
    })

@login_required
def service_detail(request, service_id):
    if not can_manage_services(request.user) and not is_sales_manager(request.user):
        return deny_access(request, 'У вас нет прав на просмотр услуги.')

    service = get_object_or_404(Service.objects.select_related('contractor', 'category'), id=service_id)
    next_url = request.GET.get('next')

    return render(request, 'core/service_detail.html', {
        'service': service,
        'next_url': next_url,
    })

@login_required
def service_create(request):
    if not can_manage_services(request.user):
        return deny_access(request, 'У вас нет прав на управление услугами.')

    if request.method == 'POST':
        query = request.POST.get('q', '').strip()
        selected_category = request.POST.get('category', '').strip()
    else:
        query = request.GET.get('q', '').strip()
        selected_category = request.GET.get('category', '').strip()

    contractors = get_contractors_for_service_create(query=query)
    categories = get_service_categories()
    next_url = get_next_url(request)

    if request.method == 'POST':
        form = ServiceCreateForm(request.POST)
        form.fields['contractor'].queryset = contractors

        if form.is_valid():
            form.save()
            messages.success(request, 'Услуга создана.')
            return redirect('service_list')
    else:
        form = ServiceCreateForm()
        form.fields['contractor'].queryset = contractors

    return render(request, 'core/service_form.html', {
        'form': form,
        'is_edit': False,
        'query': query,
        'categories': categories,
        'selected_category': selected_category,
        'next_url': next_url,
        'current_full_path': request.get_full_path(),
    })

@login_required
def service_create_for_contractor(request, contractor_id):
    if not can_manage_services(request.user):
        return deny_access(request, 'У вас нет прав на управление услугами.')

    contractor = get_object_or_404(Contractor, id=contractor_id)
    next_url = get_next_url(request)

    if request.method == 'POST':
        form = ServiceForContractorCreateForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.contractor = contractor
            service.save()

            messages.success(
                request,
                f'Услуга "{service.name}" добавлена для поставщика "{contractor.name}".'
            )

            if next_url:
                return redirect(next_url)

            return redirect('contractor_detail', contractor_id=contractor.id)
    else:
        form = ServiceForContractorCreateForm()

    return render(request, 'core/service_form.html', {
        'form': form,
        'is_edit': False,
        'contractor': contractor,
        'is_contractor_context': True,
        'next_url': next_url,
    })

@login_required
def service_update(request, service_id):
    if not can_manage_services(request.user):
        return deny_access(request, 'У вас нет прав на управление услугами.')

    service = get_object_or_404(Service, id=service_id)
    next_url = get_next_url(request)

    old_cost_price = service.cost_price

    if request.method == 'POST':
        form = ServiceUpdateForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save()
            handle_service_cost_change(service, old_cost_price)

            messages.success(request, 'Услуга обновлена.')
            return redirect(next_url or 'service_list')
    else:
        form = ServiceUpdateForm(instance=service)

    return render(request, 'core/service_form.html', {
        'form': form,
        'is_edit': True,
        'service': service,
        'next_url': next_url,
        'current_full_path': request.get_full_path(),
    })

@login_required
def service_delete(request, service_id):
    if not can_manage_services(request.user):
        return deny_access(request, 'У вас нет прав на управление услугами.')

    service = get_object_or_404(Service, id=service_id)
    next_url = get_next_url(request)

    is_used = EstimateItem.objects.filter(service=service).exists()

    if is_used:
        messages.error(
            request,
            f'Услугу "{service.name}" нельзя удалить, потому что она уже используется в сметах.'
        )
        return redirect(next_url or 'service_list')

    if request.method == 'POST':
        service.delete()
        messages.success(request, f'Услуга "{service.name}" удалена.')
        return redirect(next_url or 'service_list')

    return render(request, 'core/service_confirm_delete.html', {
        'service': service,
        'next_url': next_url,
    })