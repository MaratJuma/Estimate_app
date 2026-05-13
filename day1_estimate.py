def print_estimate(services):
    total_cost = 0
    total_client = 0

    for service in services:
        line_cost = service["cost_price"] * service["qty"]
        line_client = service["client_price"] * service["qty"]

        total_cost += line_cost
        total_client += line_client

        print(f"{service['name']}:")
        print(f"  Категория: {service['category']}")
        print(f"  Количество: {service['qty']}")
        print(f"  Себестоимость за единицу: {service['cost_price']}")
        print(f"  Цена для клиента за единицу: {service['client_price']}")
        print(f"  Итого себестоимость: {line_cost}")
        print(f"  Итого клиенту: {line_client}")
        print()

    print("-" * 40)
    print(f"Итого себестоимость: {total_cost}")
    print(f"Итого для клиента: {total_client}")
    print(f"Маржа: {total_client - total_cost}")
    if total_client != 0:
        print(f"Процент маржи: {(total_client - total_cost)/total_client*100}")


services = [
    {"name": "Аренда катера", "category": "техника","cost_price": 15000, "client_price": 20000, "qty": 2},
    {"name": "Гид", "category": "персонал","cost_price": 5000, "client_price": 7000, "qty": 3},
    {"name": "Питание", "category": "сервис", "cost_price": 2500, "client_price": 4000, "qty": 6},
    {"name": "Трансфер","category": "сервис", "cost_price": 1200, "client_price": 1500, "qty": 2},
    {"name": "Шлюхи","category": "сервис", "cost_price": 20000, "client_price": 30000, "qty": 10}
]

print_estimate(services)