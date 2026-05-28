from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from ..forms import EstimateItemQtyForm, EstimateItemUpdateForm
from ..models import EstimateDay, EstimateItem, Service
from ..permissions import can_edit_estimates, deny_access
from ..selectors.services import (
    get_active_services_for_estimate_item_queryset,
    get_contractor_by_id,
    get_contractors_for_estimate_item_filter,
    get_service_categories,
    get_service_category_by_id,
)
from ..services.estimate_items import (
    create_estimate_item_from_service,
    update_estimate_item,
)
from ..utils import build_pagination_slots, build_query_params_without_page

@login_required
def estimate_item_create(request, day_id):
    if not can_edit_estimates(request.user):
        return deny_access(request, 'У вас нет прав на редактирование смет.')

    day = get_object_or_404(EstimateDay, id=day_id)
    estimate = day.estimate

    if estimate.is_approved:
        messages.error(request, f'Смета #{estimate.id} утверждена. Добавление позиций запрещено.')
        return redirect('estimate_detail', estimate_id=estimate.id)

    query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()
    selected_contractor = request.GET.get('contractor', '').strip()

    services = get_active_services_for_estimate_item_queryset(
        query=query,
        category_id=selected_category,
        contractor_id=selected_contractor,
    )

    categories = get_service_categories()
    contractors = get_contractors_for_estimate_item_filter(
        query=query,
        category_id=selected_category,
    )

    selected_category_obj = get_service_category_by_id(selected_category)
    selected_contractor_obj = get_contractor_by_id(selected_contractor)

    paginator = Paginator(services, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    pagination_slots = build_pagination_slots(page_obj)

    return render(request, 'core/estimate_item_form.html', {
        'estimate': estimate,
        'day': day,
        'services': page_obj,
        'page_obj': page_obj,
        'pagination_slots': pagination_slots,
        'query_params': build_query_params_without_page(request),
        'query': query,
        'categories': categories,
        'selected_category': selected_category,
        'selected_category_obj': selected_category_obj,
        'selected_category_name': selected_category_obj.name if selected_category_obj else '',
        'contractors': contractors,
        'selected_contractor': selected_contractor,
        'selected_contractor_obj': selected_contractor_obj,
        'current_full_path': request.get_full_path(),
    })

@login_required
def estimate_item_create_for_service(request, day_id, service_id):
    if not can_edit_estimates(request.user):
        return deny_access(request, 'У вас нет прав на редактирование смет.')

    day = get_object_or_404(EstimateDay, id=day_id)
    estimate = day.estimate
    service = get_object_or_404(Service.objects.select_related('contractor'), id=service_id, is_active=True)

    if estimate.is_approved:
        messages.error(request, f'Смета #{estimate.id} утверждена. Добавление позиций запрещено.')
        return redirect('estimate_detail', estimate_id=estimate.id)

    if request.method == 'POST':
        form = EstimateItemQtyForm(request.POST)
        if form.is_valid():
            create_estimate_item_from_service(
                day=day,
                service=service,
                qty=form.cleaned_data['qty'],
            )

            messages.success(request, f'Услуга "{service.name}" добавлена в смету.')
            return redirect('estimate_detail', estimate_id=estimate.id)
    else:
        form = EstimateItemQtyForm()

    return render(request, 'core/estimate_item_add_selected_service.html', {
        'form': form,
        'estimate': estimate,
        'day': day,
        'service': service,
    })

@login_required
def estimate_item_update(request, item_id):
    if not can_edit_estimates(request.user):
        return deny_access(request, 'У вас нет прав на редактирование смет.')

    item = get_object_or_404(EstimateItem, id=item_id)
    estimate = item.estimate_day.estimate

    if estimate.is_approved:
        messages.error(request, f'Смета #{estimate.id} утверждена. Редактирование позиций запрещено.')
        return redirect('estimate_detail', estimate_id=estimate.id)

    display_cost_price = item.cost_price

    if request.method == 'POST':
        form = EstimateItemUpdateForm(request.POST, instance=item)
        if form.is_valid():
            update_estimate_item(
                item=item,
                qty=form.cleaned_data['qty'],
                client_price=form.cleaned_data['client_price'],
            )

            messages.success(request, 'Позиция сметы обновлена.')
            return redirect('estimate_detail', estimate_id=estimate.id)
    else:
        form = EstimateItemUpdateForm(instance=item)

    return render(request, 'core/estimate_item_edit_form.html', {
        'form': form,
        'estimate': estimate,
        'day': item.estimate_day,
        'item': item,
        'is_edit': True,
        'display_cost_price': display_cost_price,
    })

@login_required
def estimate_item_delete(request, item_id):
    if not can_edit_estimates(request.user):
        return deny_access(request, 'У вас нет прав на редактирование смет.')

    item = get_object_or_404(EstimateItem, id=item_id)
    estimate_id = item.estimate_day.estimate.id
    estimate = item.estimate_day.estimate

    if estimate.is_approved:
        messages.error(request, f'Смета #{estimate.id} утверждена. Удаление позиций запрещено.')
        return redirect('estimate_detail', estimate_id=estimate.id)

    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Позиция удалена.')
        return redirect('estimate_detail', estimate_id=estimate_id)

    return render(request, 'core/estimate_item_confirm_delete.html', {
        'item': item,
    })