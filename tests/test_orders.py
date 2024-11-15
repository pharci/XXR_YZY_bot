from tortoise import Tortoise, run_async
from decimal import Decimal
from app.db.models.order import Order, OrderStatus
from tortoise import Tortoise
from app.db.db import init_db, close_db
import random
from app.crud.order import create_order
from app.crud.user import get_user
from app.schemas.order import OrderCreate



async def test():
    await init_db()

    user = await get_user(787640915)

    for _ in range(100000):        
        order_data = OrderCreate(
            user=user,
            status=OrderStatus.CREATING,
            contact_method="number",
            currency="RUB",
            amount=Decimal("4000.00"),
            exchange_currency="CNY",
            exchange_rate=Decimal("0.0135")
            )
        await create_order(order_data)

    for _ in range(100000):           
        order_data = OrderCreate(
            user=user,
            status=OrderStatus.PROCESSING,
            contact_method="number",
            currency="RUB",
            amount=Decimal("4000.00"),
            exchange_currency="CNY",
            exchange_rate=Decimal("0.0135")
            )
        await create_order(order_data)

    for _ in range(100000):        
        order_data = OrderCreate(
            user=user,
            status=OrderStatus.COMPLETED,
            contact_method="number",
            currency="RUB",
            amount=Decimal("4000.00"),
            exchange_currency="CNY",
            exchange_rate=Decimal("0.0135")
            )
        await create_order(order_data)

    for _ in range(100000):       
        order_data = OrderCreate(
            user=user,
            status=OrderStatus.CANCELED,
            contact_method="number",
            currency="RUB",
            amount=Decimal("4000.00"),
            exchange_currency="CNY",
            exchange_rate=Decimal("0.0135")
            )
        await create_order(order_data)

    await close_db()

run_async(test())

print("Тестовые заказы успешно созданы.")

