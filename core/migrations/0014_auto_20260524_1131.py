from django.db import migrations


def copy_contractor_category_to_service(apps, schema_editor):
    Service = apps.get_model('core', 'Service')

    for service in Service.objects.select_related('contractor').all():
        service.category = service.contractor.category or ''
        service.save(update_fields=['category'])


def reverse_copy_service_category_to_contractor(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20260524_1130'),
    ]

    operations = [
        migrations.RunPython(
            copy_contractor_category_to_service,
            reverse_copy_service_category_to_contractor,
        ),
    ]