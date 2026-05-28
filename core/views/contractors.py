from urllib.parse import urlencode

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from ..forms import ContractorForm
from ..models import Contractor
from ..permissions import can_manage_contractors, deny_access
from ..selectors.contractors import (
    get_contractor_list_queryset,
    get_contractor_category_by_id,
)
from ..selectors.services import get_service_categories
from ..utils import build_pagination_slots, build_query_params_without_page, get_next_url

@login_required
def contractor_list(request):
    query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()

    contractors = get_contractor_list_queryset(
        query=query,
        category_id=selected_category,
    )

    categories = get_service_categories()
    selected_category_obj = get_contractor_category_by_id(selected_category)

    paginator = Paginator(contractors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    pagination_slots = build_pagination_slots(page_obj)

    return render(request, 'core/contractor_list.html', {
        'contractors': page_obj,
        'page_obj': page_obj,
        'pagination_slots': pagination_slots,
        'query': query,
        'categories': categories,
        'selected_category': selected_category,
        'selected_category_obj': selected_category_obj,
        'selected_category_name': selected_category_obj.name if selected_category_obj else '',
        'current_full_path': request.get_full_path(),
        'query_params': build_query_params_without_page(request),
    })

@login_required
def contractor_detail(request, contractor_id):
    contractor = get_object_or_404(Contractor, id=contractor_id)
    services = contractor.services.all().order_by('name', 'id')
    next_url = request.GET.get('next')

    contractor_detail_base_url = reverse('contractor_detail', args=[contractor.id])
    contractor_detail_return_url = contractor_detail_base_url

    if next_url:
        contractor_detail_return_url = f'{contractor_detail_base_url}?{urlencode({"next": next_url})}'

    return render(request, 'core/contractor_detail.html', {
        'contractor': contractor,
        'services': services,
        'next_url': next_url,
        'contractor_detail_base_url': contractor_detail_base_url,
        'contractor_detail_return_url': contractor_detail_return_url,
    })

@login_required
def contractor_create(request):
    if not can_manage_contractors(request.user):
        return deny_access(request, 'У вас нет прав на управление поставщиками.')

    next_url = get_next_url(request)

    if request.method == 'POST':
        form = ContractorForm(request.POST)
        if form.is_valid():
            contractor = form.save()
            messages.success(request, f'Поставщик "{contractor.name}" добавлен.')

            detail_url = reverse('contractor_detail', args=[contractor.id])

            if next_url:
                return redirect(f'{detail_url}?{urlencode({"next": next_url})}')

            return redirect('contractor_detail', contractor_id=contractor.id)
    else:
        form = ContractorForm()

    return render(request, 'core/contractor_form.html', {
        'form': form,
        'is_edit': False,
        'next_url': next_url,
        'current_full_path': request.get_full_path(),
    })

@login_required
def contractor_update(request, contractor_id):
    if not can_manage_contractors(request.user):
        return deny_access(request, 'У вас нет прав на управление поставщиками.')

    contractor = get_object_or_404(Contractor, id=contractor_id)
    next_url = get_next_url(request)

    if request.method == 'POST':
        form = ContractorForm(request.POST, instance=contractor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Поставщик "{contractor.name}" обновлён.')

            if next_url:
                return redirect(next_url)

            return redirect('contractor_detail', contractor_id=contractor.id)
    else:
        form = ContractorForm(instance=contractor)

    return render(request, 'core/contractor_form.html', {
        'form': form,
        'is_edit': True,
        'contractor': contractor,
        'next_url': next_url,
        'current_full_path': request.get_full_path(),
    })