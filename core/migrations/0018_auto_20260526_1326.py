from django.db import migrations


def fill_service_categories(apps, schema_editor):
    Service = apps.get_model('core', 'Service')
    ServiceCategory = apps.get_model('core', 'ServiceCategory')

    existing_names = set(
        Service.objects.exclude(category__isnull=True)
        .exclude(category__exact='')
        .values_list('category', flat=True)
        .distinct()
    )

    category_map = {}

    for name in existing_names:
        category_obj, created = ServiceCategory.objects.get_or_create(
            name=name.strip(),
            defaults={
                'is_active': True,
                'sort_order': 0,
            }
        )
        category_map[name] = category_obj

    for service in Service.objects.all():
        raw_name = (service.category or '').strip()
        if raw_name:
            service.category_ref = category_map.get(raw_name)
            service.save(update_fields=['category_ref'])


def reverse_fill_service_categories(apps, schema_editor):
    Service = apps.get_model('core', 'Service')

    for service in Service.objects.select_related('category_ref').all():
        if service.category_ref:
            service.category = service.category_ref.name
            service.save(update_fields=['category'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_servicecategory_service_category_ref'),
    ]

    operations = [
        migrations.RunPython(
            fill_service_categories,
            reverse_fill_service_categories,
        ),
    ]