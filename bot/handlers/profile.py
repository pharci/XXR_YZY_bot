from aiogram import Router, types
from admin.api import *
from ..keyboards import *
from aiogram import F, Router
from ..main import dp, bot
from datetime import datetime, timedelta

router = Router()

@dp.callback_query(F.data == "Profile")
async def start(call: types.CallbackQuery):
    user = await add_or_get_user(call.message.chat.username, call.message.chat.id)

    await call.message.edit_text(
        f"ID: {user.user_id}\nUsername: @{user.username}\nДата регистрации: {(user.date_created + timedelta(hours=3)).strftime("%d.%m.%Y %H:%M:%S")}", 
        reply_markup=autokey({'Последние 5 заказов': 'ShowOrders', 'Назад': 'start'})
    )

@dp.callback_query(F.data == "ShowOrders")
async def start(call: types.CallbackQuery):
    user = await add_or_get_user(call.message.chat.username, call.message.chat.id)
    orders = await get_last_5_orders(user)

    if orders:
        orders_text = "Ваши последние 5 заказов:\n\n"
        for order in orders:
            orders_text += (
                f"Заказ #{order.order_id} - {(order.date_created + timedelta(hours=3)).strftime("%d.%m.%Y %H:%M:%S")}\n"
                f"  Сумма: {order.amount} {order.currency}\n"
                f"  Получено: {round(order.amount / order.exchange_rate, 2)} {order.exchange_currency}\n"
                f"  Курс обмена: {order.exchange_rate}\n\n"
            )
    else:
        orders_text = "У вас пока нет заказов."

    await call.message.edit_text(
        orders_text, reply_markup=autokey({'Назад': 'Profile', 'Меню': 'start'})
    )