from django.db import transaction


@transaction.atomic
def delete_service_category_if_empty(category):
    if category.services.exists():
        raise ValueError('Нельзя удалить категорию, в которой есть услуги.')
    category.delete()