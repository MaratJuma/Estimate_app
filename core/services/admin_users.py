from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

User = get_user_model()

ROLE_ADMIN = 'admin'
ROLE_PRODUCTION_MANAGER = 'production_manager'
ROLE_SALES_MANAGER = 'sales_manager'

ROLE_CHOICES = (
    (ROLE_ADMIN, 'Администратор'),
    (ROLE_PRODUCTION_MANAGER, 'Отдел производства'),
    (ROLE_SALES_MANAGER, 'Отдел продаж'),
)

ROLE_GROUP_NAMES = {ROLE_PRODUCTION_MANAGER, ROLE_SALES_MANAGER}


def get_or_create_role_group(role_name):
    group, _ = Group.objects.get_or_create(name=role_name)
    return group


def clear_role_groups(user):
    user.groups.remove(*user.groups.filter(name__in=ROLE_GROUP_NAMES))


def get_user_role(user):
    if user.is_superuser:
        return ROLE_ADMIN

    if user.groups.filter(name=ROLE_PRODUCTION_MANAGER).exists():
        return ROLE_PRODUCTION_MANAGER

    if user.groups.filter(name=ROLE_SALES_MANAGER).exists():
        return ROLE_SALES_MANAGER

    return ''


@transaction.atomic
def assign_user_role(user, role):
    clear_role_groups(user)

    if role == ROLE_ADMIN:
        user.is_superuser = True
        user.is_staff = True
        user.save(update_fields=['is_superuser', 'is_staff'])
        return user

    user.is_superuser = False
    user.is_staff = False
    user.save(update_fields=['is_superuser', 'is_staff'])

    if role in ROLE_GROUP_NAMES:
        group = get_or_create_role_group(role)
        user.groups.add(group)

    return user


@transaction.atomic
def create_user_with_role(
    *,
    username,
    password,
    first_name='',
    last_name='',
    is_active=True,
    role='',
):
    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=is_active,
    )
    assign_user_role(user, role)
    return user


@transaction.atomic
def update_user_with_role(
    user,
    *,
    username,
    first_name='',
    last_name='',
    is_active=True,
    role='',
    new_password='',
):
    user.username = username
    user.first_name = first_name
    user.last_name = last_name
    user.is_active = is_active

    if new_password:
        user.set_password(new_password)

    user.save()
    assign_user_role(user, role)
    return user


def can_delete_user(target_user, acting_user):
    if target_user.id == acting_user.id:
        return False
    return True


@transaction.atomic
def delete_user_with_guards(target_user, acting_user):
    if target_user.id == acting_user.id:
        raise ValueError('Нельзя удалить собственного пользователя.')

    if target_user.is_superuser:
        admin_count = User.objects.filter(is_superuser=True).count()
        if admin_count <= 1:
            raise ValueError('Нельзя удалить последнего администратора.')

    target_user.delete()