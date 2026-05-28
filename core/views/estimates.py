from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from ..forms import EstimateForm
from ..models import Estimate, EstimateItem
from ..permissions import (
    can_approve_estimates,
    can_edit_estimates,
    can_view_estimates,
    can_edit_estimate,
    can_duplicate_estimate,
    can_delete_estimate,
    deny_access,
)
from ..selectors.estimates import (
    attach_estimate_detail_day_summary,
    attach_estimate_list_summary,
    get_estimate_detail_queryset,
    get_estimate_list_queryset,
)
from ..services.estimates import (
    approve_estimate,
    create_estimate_with_first_day,
    delete_empty_estimate,
    duplicate_estimate,
)
from ..utils import build_pagination_slots, build_query_params_without_page

@login_required
def estimate_list(request):
    if not can_view_estimates(request.user):
        return deny_access(request, 'У вас нет прав на просмотр смет.')

    query = request.GET.get('q', '').strip()

    estimates = get_estimate_list_queryset(query=query)

    paginator = Paginator(estimates, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for estimate in page_obj:
        attach_estimate_list_summary(estimate)

    pagination_slots = build_pagination_slots(page_obj)

    return render(request, 'core/estimate_list.html', {
        'estimates': page_obj,
        'page_obj': page_obj,
        'pagination_slots': pagination_slots,
        'query': query,
        'query_params': build_query_params_without_page(request),
    })

@login_required
def estimate_detail(request, estimate_id):
    if not can_view_estimates(request.user):
        return deny_access(request, 'У вас нет прав на просмотр смет.')

    estimate = get_object_or_404(get_estimate_detail_queryset(), id=estimate_id)
    days = estimate.days.all().order_by('day_number')

    summary = attach_estimate_detail_day_summary(days)
    has_items = EstimateItem.objects.filter(estimate_day__estimate=estimate).exists()

    can_edit_estimate_ui = can_edit_estimate(request.user, estimate)
    can_duplicate_estimate_ui = can_duplicate_estimate(request.user, estimate)
    can_delete_estimate_ui = can_delete_estimate(request.user, estimate)
    can_show_delete_button = (not estimate.is_approved) and (not has_items)

    return render(request, 'core/estimate_detail.html', {
        'estimate': estimate,
        'days': summary['days'],
        'total_cost': summary['total_cost'],
        'total_client': summary['total_client'],
        'margin': summary['margin'],
        'margin_percent': summary['margin_percent'],
        'days_count': days.count(),
        'current_full_path': request.get_full_path(),
        'can_edit_estimate_ui': can_edit_estimate_ui,
        'can_duplicate_estimate_ui': can_duplicate_estimate_ui,
        'can_delete_estimate_ui': can_delete_estimate_ui,
        'can_show_delete_button': can_show_delete_button,
    })

@login_required
def estimate_create(request):
    if not can_edit_estimates(request.user):
        return deny_access(request, 'У вас нет прав на создание смет.')

    if request.method == 'POST':
        form = EstimateForm(request.POST)
        if form.is_valid():
            estimate = create_estimate_with_first_day(
                client_name=form.cleaned_data['client_name'],
                comment=form.cleaned_data.get('comment', ''),
                user=request.user,
            )
            return redirect('estimate_detail', estimate_id=estimate.id)
    else:
        form = EstimateForm()

    return render(request, 'core/estimate_form.html', {
        'form': form,
        'is_edit': False,
        'title': 'Создание сметы',
    })

@login_required
def estimate_update(request, estimate_id):
    estimate = get_object_or_404(Estimate, id=estimate_id)

    if not can_edit_estimate(request.user, estimate):
        return deny_access(request, 'У вас нет прав на редактирование этой сметы.')

    if estimate.is_approved:
        messages.error(request, f'Смета #{estimate.id} утверждена и недоступна для редактирования.')
        return redirect('estimate_detail', estimate_id=estimate.id)

    has_items = EstimateItem.objects.filter(estimate_day__estimate=estimate).exists()
    can_delete_estimate_ui = can_delete_estimate(request.user, estimate)
    can_show_delete_button = not has_items

    if request.method == 'POST':
        form = EstimateForm(request.POST, instance=estimate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Смета обновлена.')
            return redirect('estimate_detail', estimate_id=estimate.id)
    else:
        form = EstimateForm(instance=estimate)

    return render(request, 'core/estimate_form.html', {
        'form': form,
        'is_edit': True,
        'estimate': estimate,
        'can_delete_estimate_ui': can_delete_estimate_ui,
        'can_show_delete_button': can_show_delete_button,
    })

@login_required
def estimate_duplicate(request, estimate_id):
    source_estimate = get_object_or_404(
        get_estimate_detail_queryset(),
        id=estimate_id
    )

    if not can_duplicate_estimate(request.user, source_estimate):
        return deny_access(request, 'У вас нет прав на дублирование смет.')

    if request.method == 'POST':
        new_estimate = duplicate_estimate(source_estimate, user=request.user)

        messages.success(
            request,
            f'Смета #{source_estimate.id} успешно скопирована. '
            f'Открыта форма редактирования новой сметы #{new_estimate.id}.'
        )
        return redirect('estimate_update', estimate_id=new_estimate.id)

    return render(request, 'core/estimate_duplicate_confirm.html', {
        'estimate': source_estimate,
    })

@login_required
def estimate_delete(request, estimate_id):
    estimate = get_object_or_404(Estimate, id=estimate_id)

    if not can_delete_estimate(request.user, estimate):
        return deny_access(request, 'У вас нет прав на удаление этой сметы.')

    has_items = EstimateItem.objects.filter(estimate_day__estimate=estimate).exists()
    if estimate.is_approved or has_items:
        messages.error(
            request,
            'Удалить можно только неутверждённую смету без позиций.'
        )
        return redirect('estimate_update', estimate_id=estimate.id)

    if request.method == 'POST':
        try:
            estimate_number = estimate.id
            delete_empty_estimate(estimate)
            messages.success(request, f'Смета #{estimate_number} удалена.')
            return redirect('estimate_list')
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect('estimate_update', estimate_id=estimate.id)

    return render(request, 'core/estimate_confirm_delete.html', {
        'estimate': estimate,
    })

@login_required
def estimate_approve(request, estimate_id):
    if not can_approve_estimates(request.user):
        return deny_access(request, 'У вас нет прав на утверждение смет.')

    estimate = get_object_or_404(Estimate, id=estimate_id)

    if estimate.is_approved:
        messages.info(request, f'Смета #{estimate.id} уже утверждена.')
        return redirect('estimate_detail', estimate_id=estimate.id)

    if request.method == 'POST':
        approve_estimate(estimate)
        messages.success(request, f'Смета #{estimate.id} утверждена. Редактирование заблокировано.')
        return redirect('estimate_detail', estimate_id=estimate.id)

    return render(request, 'core/estimate_approve_confirm.html', {
        'estimate': estimate,
    })