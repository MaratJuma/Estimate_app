from django.contrib import messages
from django.shortcuts import render

from ..forms import DatabaseImportForm
from ..permissions import can_manage_admin_panel, deny_access
from ..services.imports import (
    EXPECTED_HEADERS,
    import_services_from_excel,
    preview_services_import,
)


def admin_import_database(request):
    if not can_manage_admin_panel(request.user):
        return deny_access(request, 'У вас нет прав на импорт данных.')

    import_result = None

    if request.method == 'POST':
        form = DatabaseImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            dry_run = form.cleaned_data.get('dry_run', False)

            try:
                if dry_run:
                    import_result = preview_services_import(uploaded_file)
                    if import_result['errors']:
                        messages.warning(
                            request,
                            'Проверка завершена с ошибками. Проверьте отчёт ниже.'
                        )
                    else:
                        messages.success(
                            request,
                            'Проверка успешно завершена. Данные в базу не записаны.'
                        )
                else:
                    import_result = import_services_from_excel(uploaded_file)
                    if import_result['errors']:
                        messages.warning(
                            request,
                            'Импорт завершён с ошибками. Проверьте отчёт ниже.'
                        )
                    else:
                        messages.success(request, 'Импорт успешно завершён.')
            except Exception as exc:
                messages.error(request, f'Ошибка импорта: {exc}')
    else:
        form = DatabaseImportForm(initial={'dry_run': True})

    return render(request, 'core/admin_import.html', {
        'form': form,
        'expected_headers': EXPECTED_HEADERS,
        'import_result': import_result,
    })