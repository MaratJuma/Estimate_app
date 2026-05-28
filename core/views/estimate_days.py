from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from ..forms import EstimateDayCreateForm, EstimateDayUpdateForm
from ..models import Estimate, EstimateDay
from ..permissions import can_edit_estimates, deny_access
from ..services.estimate_days import create_next_estimate_day, delete_day_and_renumber

@login_required
def estimate_day_create(request, estimate_id):
    if not can_edit_estimates(request.user):
        return deny_access(request, 'У вас нет прав на редактирование смет.')

    estimate = get_object_or_404(Estimate, id=estimate_id)

    if estimate.is_approved:
        messages.error(request, f'Смета #{estimate.id} утверждена. Добавление дней запрещено.')
        return redirect('estimate_detail', estimate_id=estimate.id)

    if request.method == 'POST':
        form = EstimateDayCreateForm(request.POST)
        if form.is_valid():
            day = create_next_estimate_day(
                estimate=estimate,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
            )

            messages.success(request, f'День {day.day_number} добавлен.')
            return redirect('estimate_detail', estimate_id=estimate.id)
    else:
        form = EstimateDayCreateForm()

    return render(request, 'core/estimate_day_form.html', {
        'form': form,
        'estimate': estimate,
        'is_edit': False,
    })

@login_required
def estimate_day_update(request, day_id):
    if not can_edit_estimates(request.user):
        return deny_access(request, 'У вас нет прав на редактирование смет.')

    day = get_object_or_404(EstimateDay, id=day_id)
    estimate = day.estimate

    if estimate.is_approved:
        messages.error(request, f'Смета #{estimate.id} утверждена. Редактирование дней запрещено.')
        return redirect('estimate_detail', estimate_id=estimate.id)

    if request.method == 'POST':
        form = EstimateDayUpdateForm(request.POST, instance=day)
        if form.is_valid():
            form.save()
            return redirect('estimate_detail', estimate_id=estimate.id)
    else:
        form = EstimateDayUpdateForm(instance=day)

    return render(request, 'core/estimate_day_form.html', {
        'form': form,
        'estimate': estimate,
        'day': day,
        'is_edit': True,
    })

@login_required
def estimate_day_delete(request, day_id):
    if not can_edit_estimates(request.user):
        return deny_access(request, 'У вас нет прав на редактирование смет.')

    day = get_object_or_404(EstimateDay, id=day_id)
    estimate = day.estimate

    if estimate.is_approved:
        messages.error(request, f'Смета #{estimate.id} утверждена. Удаление дней запрещено.')
        return redirect('estimate_detail', estimate_id=estimate.id)

    if day.items.exists():
        messages.error(
            request,
            f'День {day.day_number} нельзя удалить, потому что в нём есть позиции.'
        )
        return redirect('estimate_detail', estimate_id=estimate.id)

    if request.method == 'POST':
        deleted_day_number = delete_day_and_renumber(day)
        messages.success(request, f'День {deleted_day_number} удалён.')
        return redirect('estimate_detail', estimate_id=estimate.id)

    return render(request, 'core/estimate_day_confirm_delete.html', {
        'day': day,
        'estimate': estimate,
    })