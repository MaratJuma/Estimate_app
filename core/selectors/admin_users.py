from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.contrib.auth.models import Group

User = get_user_model()


def get_admin_user_list_queryset():
    return (
        User.objects
        .prefetch_related(
            Prefetch('groups', queryset=Group.objects.order_by('name'))
        )
        .order_by('username', 'id')
    )


def get_user_with_groups(user_id):
    return (
        User.objects
        .prefetch_related('groups')
        .filter(id=user_id)
        .first()
    )