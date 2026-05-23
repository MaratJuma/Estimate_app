def build_pagination_slots(page_obj, window=7):
    current = page_obj.number
    total = page_obj.paginator.num_pages

    if total <= window:
        slots = list(range(1, total + 1))
        while len(slots) < window:
            slots.append(None)
        return slots

    if current <= 4:
        return [1, 2, 3, 4, 5, 'dots', total]

    if current >= total - 3:
        return [1, 'dots', total - 4, total - 3, total - 2, total - 1, total]

    return [1, 'dots', current - 1, current, current + 1, 'dots', total]