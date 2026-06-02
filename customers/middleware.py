from django.http import HttpResponseForbidden
from django.shortcuts import render


class SuspendedTenantMiddleware:
    """
    Блокирует доступ к tenant-приложению, если tenant помечен как неактивный.
    Работает только для tenant schema. Public schema не затрагивает.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = getattr(request, 'tenant', None)

        if tenant is not None:
            schema_name = getattr(tenant, 'schema_name', None)
            is_active = getattr(tenant, 'is_active', True)

            if schema_name and schema_name != 'public' and not is_active:
                response = render(
                    request,
                    'core/tenant_suspended.html',
                    status=403,
                    context={
                        'tenant': tenant,
                    }
                )
                return response

        return self.get_response(request)