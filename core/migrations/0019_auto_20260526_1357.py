from django.db import migrations


def fill_service_categories(apps, schema_editor):
    Service = apps.get_model('core', 'Service')
    ServiceCategory = apps.get_model('core', 'ServiceCategory')

    # Собираем уникальные строковые категории из старого поля Service.category
    raw_names = (
        Service.objects
        .exclude(category__isnull=True)
        .exclude(category__exact='')
        .values_list('category', flat=True)
        .distinct()
    )

    category_map = {}

    for raw_name in raw_names:
        name = (raw_name or '').strip()
        if not name:
            continue

        category_obj, _ = ServiceCategory.objects.get_or_create(
            name=name,
            defaults={
                # 'is_active': True,
                'sort_order': 0,
            }
        )
        category_map[name] = category_obj

    # Проставляем category_ref у услуг
    for service in Service.objects.all():
        name = (service.category or '').strip()
        if not name:
            continue

        category_obj = category_map.get(name)
        if category_obj:
            service.category_ref_id = category_obj.id
            service.save(update_fields=['category_ref'])


def reverse_fill_service_categories(apps, schema_editor):
    Service = apps.get_model('core', 'Service')

    # Откат: вернуть строковое поле category из category_ref.name
    for service in Service.objects.select_related('category_ref').all():
        if service.category_ref:
            service.category = service.category_ref.name
            service.save(update_fields=['category'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20260526_1326'),
    ]

    operations = [
        migrations.RunPython(
            fill_service_categories,
            reverse_fill_service_categories,
        ),
    ]