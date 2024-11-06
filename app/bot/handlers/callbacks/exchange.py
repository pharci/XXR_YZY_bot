from aiogram import Router, types
from aiogram.filters import Filter
from app.bot.keyboards import *
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

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
        if not message.text.isdigit():
            await message.answer("Неверный формат, попробуйте еще раз.", reply_markup=autokey({'Отмена': 'start'}))
            return False
        return True


@router.callback_query(F.data == "Exchange")
async def currency_choice(call: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    currencies = await get_all_currencies()
    for i in currencies:
        builder.button(
            text=f"{i.currency} -> {i.exchange_currency}", callback_data=f"{i.id}"
        )

    await call.message.edit_text("Выберите обмен из доступных:", reply_markup=builder.as_markup())
    await state.set_state(Form.currency_choice)


@router.callback_query(CurrencyFilter(), Form.currency_choice)
async def currency_input(call: types.CallbackQuery, state: FSMContext):
    data = await get_currency_by_id(call.data)
    await state.update_data(currency_id=call.data)
    await state.update_data(message_id=call.message.message_id)

    await call.message.edit_text(
        f"Вы выбрали {data["currency"]} -> {data["exchange_currency"]} \n\nВыберите, в чем вы хотите ввести сумму:",
        reply_markup=autokey({f'{data["currency"]}': f'{data["currency"]}', f'{data["exchange_currency"]}': f'{data["exchange_currency"]}'})
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

    user = await add_or_get_user(message.from_user.username, message.from_user.id)
    print(user_data['amount'])
    order = await create_order(
        user, 
        message.contact.phone_number, 
        data["currency"], 
        user_data['amount'], 
        data["exchange_currency"], 
        user_data["exchange_rate"]
        )
    
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
        0: round(float(data['exchange_rate']), 2),
        250: round(float(data['exchange_rate']) - float(data["graduation_step"]), 2),
        500: round(float(data['exchange_rate']) - float(data["graduation_step"]) * 2, 2),
        1000: round(float(data['exchange_rate']) - float(data["graduation_step"]) * 3, 2),
        5000: round(float(data['exchange_rate']) - float(data["graduation_step"]) * 3.5, 2),
        10000: round(float(data['exchange_rate']) - float(data["graduation_step"]) * 4.5, 2),
    }

    user_currency = user_data["currency_input"]
    determined_rate = 0
    currency_text = ""
    # Проверяем, соответствует ли введенная валюта целевой валюте
    if user_currency == data['currency']:
        previous_min_amount = 0
        for current_min_amount, current_rate in exchange_rates.items():
            if previous_min_amount <= int(message.text) / current_rate < current_min_amount:
                determined_rate = previous_min_amount
                amount = float(message.text)

                await state.update_data(amount=amount)

                currency_text = f"{message.text} {data['currency']} -> {round(amount / float(exchange_rates[determined_rate]), 2)} {data['exchange_currency']}"
                break
            previous_min_amount = current_min_amount

    # Проверяем, соответствует ли введенная валюта валюте обмена
    elif user_currency == data['exchange_currency']:
        previous_min_amount = 0
        for current_min_amount, current_rate in exchange_rates.items():
            if previous_min_amount <= int(message.text) < current_min_amount:

                determined_rate = previous_min_amount

                amount = float(round(int(message.text) * float(exchange_rates[determined_rate]), 2))
                await state.update_data(amount=amount)

                currency_text = f"{message.text} {data['exchange_currency']} -> {amount} {data['currency']}"
                break
            previous_min_amount = current_min_amount

    await state.update_data(exchange_rate=exchange_rates[determined_rate])

    rates_text = "\n".join([f"От {amount} {data['exchange_currency']}  - {rate} {data['currency']}" for amount, rate in exchange_rates.items()])

    await message.answer(
        text=f"Конвертация по курсу - {exchange_rates[determined_rate]} {data['currency']}:\n\n"
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