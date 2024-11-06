from models import *
import random


async def get_currency_by_id(currency_id: int):
    try:
        currency_data = await Sysdata.get(id=currency_id)  # Получаем запись по ID
        return {
            "id": currency_data.id,
            "currency": currency_data.currency,
            "graduation_step": str(currency_data.graduation_step),
            "exchange_currency": currency_data.exchange_currency,
            "exchange_rate": str(currency_data.exchange_rate)  # Конвертируем Decimal в строку для JSON
        }
    except:
        return None 



async def get_all_currencies():
    currencies = await Sysdata.all()
    return list(currencies)

async def create_order(user_id: int, contact_method: str, currency: str, amount: float, exchange_currency: str, exchange_rate: float):
    order_id = random.randint(10000000, 99999999)
    while await Order.filter(order_id=order_id).exists():
        order_id = random.randint(10000000, 99999999)

    order = await Order.create(
        user=user_id,
        order_id=order_id,
        contact_method=contact_method,
        currency=currency,
        amount=amount,
        exchange_currency=exchange_currency,
        exchange_rate=exchange_rate
    )
    return order

async def get_last_5_orders(user: User):
    last_orders = await Order.filter(user=user).order_by('-id').limit(5)
    return last_orders