from app.db.models.order import Order
from app.schemas.order import OrderCreate
import random
from typing import List
from app.db.models.user import User

async def create_order(order_data: OrderCreate) -> Order:
    order_id = random.randint(10000000, 99999999)
    while await Order.filter(order_id=order_id).exists():
        order_id = random.randint(10000000, 99999999)

    order = await Order.create(
        user=order_data.user,
        order_id=order_id,
        contact_method=order_data.contact_method,
        currency=order_data.currency,
        amount=order_data.amount,
        exchange_currency=order_data.exchange_currency,
        exchange_rate=order_data.exchange_rate
    )
    return order

async def get_last_5_orders(user: User) -> List[Order]:
    return await Order.filter(user=user).order_by('-id').limit(5)

async def get_all_orders() -> List[Order]:
    return await Order.all()

async def get_order_by_id(order_id: int) -> Order:
    return await Order.get(order_id=order_id)

async def get_all_user_orders(user: User) -> List[Order]:
    return await Order.filter(user=user)