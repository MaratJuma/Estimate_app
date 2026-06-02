from django.utils import timezone
from django.db import transaction
from django.db.models import Max

from core.models import Estimate, EstimateDay, EstimateItem


def get_display_manager_name(user):
    full_name = user.get_full_name().strip()
    if full_name:
        return full_name
    return user.username


def get_next_contract_estimate_number(contract_number: str) -> int:
    contract_number = contract_number.strip()

    max_number = (
        Estimate.objects
        .filter(contract_number=contract_number)
        .aggregate(max_number=Max("contract_estimate_number"))
        ["max_number"]
    )
    return 1 if max_number is None else max_number + 1


@transaction.atomic
def create_estimate_with_first_day(*, client_name, comment, contract_number, user):
    contract_number = contract_number.strip()

    estimate = Estimate.objects.create(
        client_name=client_name,
        manager_name=get_display_manager_name(user),
        created_by=user,
        comment=comment,
        contract_number=contract_number,
        contract_estimate_number=get_next_contract_estimate_number(contract_number),
    )
    EstimateDay.objects.create(estimate=estimate, day_number=1)
    return estimate


def approve_estimate(estimate):
    for day in estimate.days.all().prefetch_related('items__service'):
        for item in day.items.all():
            item.cost_price = item.service.cost_price
            item.total_cost = item.qty * item.cost_price
            item.total_client = item.qty * item.client_price
            item.save()

    estimate.is_approved = True
    estimate.approved_at = timezone.now()
    estimate.save()

    return estimate


@transaction.atomic
def duplicate_estimate(source_estimate, *, user, contract_number):
    contract_number = contract_number.strip()
    duplicator_name = get_display_manager_name(user)

    copy_note = f'Копия сметы #{source_estimate.id}. Создана пользователем: {duplicator_name}'

    if source_estimate.comment:
        new_comment = f'{source_estimate.comment}\n\n[{copy_note}]'
    else:
        new_comment = copy_note

    new_estimate = Estimate.objects.create(
        client_name=source_estimate.client_name,
        manager_name=duplicator_name,
        created_by=user,
        comment=new_comment,
        contract_number=contract_number,
        contract_estimate_number=get_next_contract_estimate_number(contract_number),
        is_approved=False,
        approved_at=None,
    )

    day_mapping = {}

    for day in source_estimate.days.all().order_by('day_number', 'id'):
        new_day = EstimateDay.objects.create(
            estimate=new_estimate,
            day_number=day.day_number,
            title=day.title,
            description=day.description,
        )
        day_mapping[day.id] = new_day

    for day in source_estimate.days.all().order_by('day_number', 'id'):
        new_day = day_mapping[day.id]

        for item in day.items.all():
            current_cost_price = item.service.cost_price
            qty = item.qty
            client_price = item.client_price

            EstimateItem.objects.create(
                estimate_day=new_day,
                service=item.service,
                qty=qty,
                cost_price=current_cost_price,
                client_price=client_price,
                total_cost=qty * current_cost_price,
                total_client=qty * client_price,
            )

    return new_estimate


def delete_empty_estimate(estimate):
    if estimate.is_approved:
        raise ValueError('Нельзя удалить утверждённую смету.')

    has_items = EstimateItem.objects.filter(estimate_day__estimate=estimate).exists()
    if has_items:
        raise ValueError('Нельзя удалить смету, в которой есть позиции.')

    estimate.delete()