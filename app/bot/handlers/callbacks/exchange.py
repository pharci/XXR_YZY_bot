from aiogram import Router, types
from aiogram.filters import Filter
from app.bot.keyboards import *
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from app.bot.keyboards.keyboards import autokey
from app.crud.sysdata import get_currency_by_id, get_all_currencies
from app.crud.order import create_order
from app.crud.user import get_user
from app.schemas.order import OrderCreate
from decimal import Decimal


router = Router()

class Form(StatesGroup):
    currency_choice = State()
    currency_input_choice = State()
    input_currency = State()
    success = State()
    contact = State()
    final = State()

class CurrencyFilter(Filter):
    async def __call__(self, callback: types.CallbackQuery):
        currencies = await get_all_currencies()  # Получаем все валюты
        for i in currencies:
            if callback.data == f"{i.id}":
                return True
        return False
    
class CurrencyInputFilter(Filter):
    async def __call__(self, message: types.Message):
        
        try:
            input_amount = Decimal(message.text)
            return True
        except:
            await message.answer("Неверный формат, попробуйте еще раз.", reply_markup=autokey({'Отмена': 'start'}))
            return False


@router.callback_query(F.data == "Exchange")
async def currency_choice(call: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    currencies = await get_all_currencies()
    for i in currencies:
        builder.button(
            text=f"{i.currency} -> {i.exchange_currency}", callback_data=f"{i.id}"
        )
    builder.adjust(1)

    await call.message.edit_text("Выберите обмен из доступных:", reply_markup=builder.as_markup())
    await state.set_state(Form.currency_choice)


@router.callback_query(CurrencyFilter(), Form.currency_choice)
async def currency_input(call: types.CallbackQuery, state: FSMContext):
    data = await get_currency_by_id(call.data)
    await state.update_data(currency_id=call.data)
    await state.update_data(message_id=call.message.message_id)

    await call.message.edit_text(
        f"Вы выбрали {data.currency} -> {data.exchange_currency} \n\nВыберите, в чем вы хотите ввести сумму:",
        reply_markup=autokey({f'{data.currency}': f'{data.currency}', f'{data.exchange_currency}': f'{data.exchange_currency}'})
        )

    await state.set_state(Form.currency_input_choice)



@router.callback_query(Form.currency_input_choice)
async def currency_input(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(currency_input=call.data)

    await call.message.edit_text(
        f"Введите сумму в {call.data}:",
        reply_markup=autokey({'Отмена': 'start'})
        )

    await state.set_state(Form.input_currency)


@router.message(F.contact, Form.contact)
async def finish(message: types.Message, state: FSMContext): 
    user_data = await state.get_data()
    data = await get_currency_by_id(user_data['currency_id'])

    user = await get_user(message.from_user.id)

    order_data = OrderCreate(
        user=user,
        contact_method=message.contact.phone_number,
        currency=data.currency,
        amount=user_data['amount'],
        exchange_currency=data.exchange_currency,
        exchange_rate=user_data["exchange_rate"]
    )
    order = await create_order(order_data)
    
    await message.answer("Создание заказа...", reply_markup=ReplyKeyboardRemove())
    await message.answer(
        text=f'Ваш заказ: №{order.order_id}',  
        reply_markup=autokey({'Профиль': 'Profile', 'Меню': 'start'})
        )


@router.message(CurrencyInputFilter(), Form.input_currency)
async def finish(message: types.Message, state: FSMContext): 
    user_data = await state.get_data()
    data = await get_currency_by_id(user_data['currency_id'])
    
    exchange_rates = {
        0: round(Decimal(data.exchange_rate), 2),
        250: round(Decimal(data.exchange_rate) - Decimal(data.graduation_step), 2),
        500: round(Decimal(data.exchange_rate) - Decimal(data.graduation_step) * Decimal(2), 2),
        1000: round(Decimal(data.exchange_rate) - Decimal(data.graduation_step) * Decimal(3), 2),
        5000: round(Decimal(data.exchange_rate) - Decimal(data.graduation_step) * Decimal(3.5), 2),
        10000: round(Decimal(data.exchange_rate) - Decimal(data.graduation_step) * Decimal(4.5), 2),
    }

    user_currency = user_data["currency_input"]
    determined_rate = 0
    currency_text = ""

    if user_currency == data.currency:
        previous_min_amount = 0
        for current_min_amount, current_rate in exchange_rates.items():
            if previous_min_amount <= Decimal(message.text) / current_rate < current_min_amount:
                determined_rate = previous_min_amount
                amount = Decimal(message.text)

                await state.update_data(amount=amount)

                currency_text = f"{message.text} {data.currency} -> {round(round(Decimal(amount), 2) / Decimal(exchange_rates[determined_rate]), 2)} {data.exchange_currency}"
                break
            previous_min_amount = current_min_amount

    elif user_currency == data.exchange_currency:
        previous_min_amount = 0
        for current_min_amount, current_rate in exchange_rates.items():
            if previous_min_amount <= Decimal(message.text) < current_min_amount:

                determined_rate = previous_min_amount

                amount = Decimal(message.text) * Decimal(exchange_rates[determined_rate])
                await state.update_data(amount=amount)

                currency_text = f"{message.text} {data.exchange_currency} -> {round(Decimal(amount), 2)} {data.currency}"
                break
            previous_min_amount = current_min_amount

    await state.update_data(exchange_rate=exchange_rates[determined_rate])

    rates_text = "\n".join([f"От {round(Decimal(amount), 2)} {data.exchange_currency}  - {rate} {data.currency}" for amount, rate in exchange_rates.items()])

    await message.answer(
        text=f"Конвертация по курсу - {exchange_rates[determined_rate]} {data.currency}:\n\n"
             f"{rates_text}\n\n"
             f"{currency_text}",

        reply_markup=autokey({'Подтверждаю': 'Success', 'Отмена': 'start'})
    )

    await state.set_state(Form.success)




@router.callback_query(F.data == "Success", Form.success)
async def currency_input(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()

    kb_list = [
        [KeyboardButton(text='Поделиться контактом', request_contact=True)],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)

    await call.message.answer(
        text = f"Нажмите кнопку ниже, чтобы поделиться телефоном: ",
        reply_markup=keyboard)

    await state.set_state(Form.contact)