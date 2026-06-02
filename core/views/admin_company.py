from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from ..forms import CompanyProfileForm
from ..models import CompanyProfile
from ..permissions import can_manage_admin_panel, deny_access


@login_required
def admin_company_update(request):
    if not can_manage_admin_panel(request.user):
        return deny_access(request, 'У вас нет прав на управление данными компании.')

    company_profile, _ = CompanyProfile.objects.get_or_create(
        id=1,
        defaults={
            'name': 'Новая компания',
            'manager_title': 'Менеджер проекта',
        }
    )

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=company_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные компании обновлены.')
            return redirect('admin_company_update')
    else:
        form = CompanyProfileForm(instance=company_profile)

    return render(request, 'core/admin_company_form.html', {
        'form': form,
        'company_profile': company_profile,
    })