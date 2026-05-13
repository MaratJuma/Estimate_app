from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()


@register.filter
def money(value):
    try:
        value = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return value

    formatted = f'{value:,.2f}'.replace(',', ' ')
    return formatted