from django.db import migrations


def copy_contractor_category_to_service(apps, schema_editor):
    Service = apps.get_model('core', 'Service')

    for service in Service.objects.select_related('contractor').all():
        service.category = service.contractor.category or ''
        service.save(update_fields=['category'])


def reverse_copy_service_category_to_contractor(apps, schema_editor):
    # Обратный перенос не делаем:
    # после новой логики у одного поставщика может быть несколько категорий услуг,
    # поэтому восстановить contractor.category однозначно нельзя.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20260524_1113'),
    ]

    operations = [
        migrations.RunPython(
            copy_contractor_category_to_service,
            reverse_copy_service_category_to_contractor,
        ),
    ]