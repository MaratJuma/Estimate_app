from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import PublicTenantRegistrationForm
from .services import provision_tenant_with_admin


def home(request):
    return render(request, "public_portal/home.html")


def register_company(request):
    if request.method == 'POST':
        form = PublicTenantRegistrationForm(request.POST)
        if form.is_valid():
            result = provision_tenant_with_admin(
                company_name=form.cleaned_data['company_name'],
                subdomain=form.cleaned_data['subdomain'],
                admin_username=form.cleaned_data['admin_username'],
                admin_email=form.cleaned_data['admin_email'],
                password=form.cleaned_data['password1'],
                base_domain=settings.TENANT_BASE_DOMAIN,
                phone=form.cleaned_data.get('phone', ''),
                company_email=form.cleaned_data.get('company_email', ''),
                website=form.cleaned_data.get('website', ''),
                address=form.cleaned_data.get('address', ''),
            )

            if settings.TENANT_BASE_DOMAIN == 'localhost':
                login_url = f'http://{result["domain"]}:8000/accounts/login/'
            else:
                login_url = f'https://{result["domain"]}/accounts/login/'

            request.session['tenant_registration_success'] = {
                'company_name': form.cleaned_data['company_name'],
                'domain': result['domain'],
                'admin_username': form.cleaned_data['admin_username'],
                'login_url': login_url,
            }

            return redirect('public_register_success')
    else:
        form = PublicTenantRegistrationForm()

    return render(request, 'public_portal/register.html', {
        'form': form,
    })


def register_success(request):
    data = request.session.get('tenant_registration_success')
    if not data:
        return redirect('public_register_company')

    return render(request, 'public_portal/register_success.html', {
        'company_name': data['company_name'],
        'domain': data['domain'],
        'admin_username': data['admin_username'],
        'login_url': data['login_url'],
    })