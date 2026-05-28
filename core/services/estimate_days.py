from django.db.models import F
from core.models import EstimateDay


def create_next_estimate_day(estimate, title='', description=''):
    last_day = estimate.days.order_by('-day_number').first()
    next_day_number = last_day.day_number + 1 if last_day else 1

    return EstimateDay.objects.create(
        estimate=estimate,
        day_number=next_day_number,
        title=title,
        description=description,
    )


def delete_day_and_renumber(day):
    estimate = day.estimate
    deleted_day_number = day.day_number

    day.delete()

    EstimateDay.objects.filter(
        estimate=estimate,
        day_number__gt=deleted_day_number
    ).update(day_number=F('day_number') - 1)

    return deleted_day_number