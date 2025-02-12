from aiogram import Router, types
from aiogram.filters import Filter
from app.bot.keyboards import *
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from app.bot.keyboards.keyboards import autokey
from decimal import Decimal
from admin_app.orders.models import Conversion, OrderType, Order, OrderStatus, Promocode, PromocodeUsage, Graduation
from admin_app.accounts.models import User
from asgiref.sync import sync_to_async
import time
import random
from app.repository import DjangoRepo
import re

router = Router()

class OrderState(StatesGroup):
    ChoosingInput = State()
    input = State()
    receiving = State()
    contact = State()
    OrderPreview = State()
    InputPromocode = State()
    CreateOrder = State()

class СonversionIdFilter(Filter):
    async def __call__(self, callback: types.CallbackQuery):
        сonversion_ids = await sync_to_async(list)(
            Conversion.objects.values_list("id", flat=True)
        )
        return callback.data in map(str, сonversion_ids)


#Выбор валютной пары
@router.callback_query(F.data == "Exchange")
async def exchange(call: types.CallbackQuery, state: FSMContext):
    user = await DjangoRepo.filter(User, telegram_id=call.message.chat.id)
    if not user[0].contact:
        return await call.message.edit_text(
            "Чтобы создать заказ, установите номер телефона в профиле.", 
            reply_markup=autokey({'Профиль': 'Profile', 'Отмена': 'start'})
        )


    builder = InlineKeyboardBuilder()
    conversions = await DjangoRepo.filter(Conversion, enabled=True)
    for i in conversions:
        builder.button(
            text=f"{i.user_currency} -> {i.exchange_currency}", callback_data=f"{i.id}"
        )
    builder.button(text="Отмена", callback_data=f"start")
    builder.adjust(1)
    await state.set_state(OrderState.ChoosingInput)
    return await call.message.edit_text("Выберите, что хотите обменять:", reply_markup=builder.as_markup())

    

#Сохраняем валютную пару и спрашиваем в чем будет ввод
@router.callback_query(СonversionIdFilter(), OrderState.ChoosingInput)
async def currency_input(call: types.CallbackQuery, state: FSMContext):
    conversion = (await DjangoRepo.filter(Conversion, id=call.data))[0]

    await state.update_data(conversion_id=call.data)

    await call.message.edit_text(
        f"Вы выбрали {conversion.user_currency} -> {conversion.exchange_currency}\n\nВвести сумму в:",
        reply_markup=autokey({f'{conversion.user_currency}': f'{conversion.user_currency}',
                            f'{conversion.exchange_currency}': f'{conversion.exchange_currency}', 
                            'Отмена': 'start'})
        )
    await state.set_state(OrderState.input)

#Сохраняем вылюту ввода и просим ввести число
@router.callback_query(OrderState.input)
async def currency_input(call: types.CallbackQuery, state: FSMContext):

    await state.update_data(input_currency=call.data)

    await call.message.edit_text(
        f"Введите сумму в {call.data}:",
        reply_markup=autokey({'Отмена': 'start'})
        )

    await state.set_state(OrderState.receiving)



async def calculation(input_currency, conversion, amount, discount=0):  
    graduations = await DjangoRepo.filter(Graduation, conversions__id=conversion.id)
    matching_graduation = None
    graduation_text = ""
    
    if input_currency != conversion.user_currency:

        for graduation in graduations:
            graduation_text += f"<b>От {graduation.amount} {conversion.exchange_currency}  — </b> {conversion.course - graduation.adjustment}\n"
            if graduation.amount <= amount:
                matching_graduation = graduation

        course = conversion.course - matching_graduation.adjustment - discount
        input = round(amount * course, 2)
        output = amount
    else:
        for graduation in graduations:
            graduation_text += f"<b>От {graduation.amount} {conversion.exchange_currency}  — </b> {conversion.course - graduation.adjustment}\n"
            if graduation.amount <= round(amount / (conversion.course - graduation.adjustment), 2):
                matching_graduation = graduation
                
        course = conversion.course - matching_graduation.adjustment - discount
        input = amount
        output = round(amount / course, 2)

    return input, output, course, graduation_text


#Принимаем введеное число
@router.message(OrderState.receiving)
async def receiving_amount(message: types.Message, state: FSMContext): 
    order_data = await state.get_data()
    conversion = (await DjangoRepo.filter(Conversion, id=order_data["conversion_id"]))[0]
    graduations = await DjangoRepo.filter(Graduation, conversions__id=conversion.id)

    minimum = min(graduations, key=lambda g: g.amount).amount #ЮАНИ exchange_currency
    minimum_second = round(minimum * conversion.course, 2) #РУБЛИ input_currency
    amount = message.text.strip() #СУММА В ЮАНЯХ ИЛИ РУБЛЯХ

    if re.fullmatch(r"-?\d+([.,]\d+)?", amount):
        amount = Decimal(amount.replace(",", "."))

        amout_for_check = amount
        if order_data["input_currency"] == conversion.user_currency:
            amout_for_check = round(amount / conversion.course, 2)

        if minimum <= amout_for_check:
            await state.update_data(amount=amount)
            await message.answer(f"Вы ввели {amount}{order_data["input_currency"]}", reply_markup=autokey({'Продолжить': 'OrderPreview', 'Отмена': 'start'}))
            await state.set_state(OrderState.OrderPreview)
        else:
            await message.answer(f"Минимум {minimum}{conversion.exchange_currency} или {minimum_second}{conversion.user_currency}", reply_markup=autokey({'Отмена': 'start'}))
    else:
        await message.answer(f"Неккоректный ввод. ", reply_markup=autokey({'Отмена': 'start'}))

#Предпросмотр заказа
@router.callback_query(F.data == "OrderPreview", OrderState.OrderPreview)
async def currency_choice(call: types.CallbackQuery, state: FSMContext):
    
    order_data = await state.get_data()
    conversion = (await DjangoRepo.filter(Conversion, id=order_data["conversion_id"]))[0]
    
    promocode = order_data.get('promocode', None)
    discount = 0
    if promocode:
        discount = (await DjangoRepo.filter(Promocode, code=promocode))[0].discount

    input, output, course, graduation_text = await calculation(order_data['input_currency'], conversion, order_data["amount"], discount)

    await state.update_data(amount_input=input)
    await state.update_data(amount_output=output)
    await state.update_data(course=course)
    await state.update_data(user_currency=conversion.user_currency)
    await state.update_data(exchange_currency=conversion.exchange_currency)

    text = f"<b>Предварительный просмотр:</b> \n\n" \
           f"<b>Тип заказа:</b> Обмен \n" \
           f"<b>Вы отдаете:</b> { round(input, 0) } {conversion.user_currency}\n" \
           f"<b>Вы получаете:</b> { round(output, 0) } {conversion.exchange_currency}\n" \
           f"<b>По курсу:</b> {course} { f"<s>{course + discount}</s>" if promocode else ""}\n" \
           f"<b>Промокод:</b> {f"{promocode} (-{discount})" if promocode else "Нет"} \n\n\n" \
           f"<b>Как рассчитывается цена?</b>\n" \
           f"{graduation_text}" \
    
    await call.message.edit_text(text, reply_markup=autokey({'Ввести промокод': 'promocode', 'Оформить заказ': 'CreateOrder', 'Отмена': 'start'}))
    await state.set_state(OrderState.CreateOrder)


#Просим ввести промокод
@router.callback_query(F.data == "promocode")
async def currency_choice(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите промокод:")
    await state.set_state(OrderState.InputPromocode)

#Принимаем промокод
@router.message(OrderState.InputPromocode)
async def receiving_amount(message: types.Message, state: FSMContext): 
    try:
        promocode = await sync_to_async(Promocode.objects.get)(code=message.text)
        await state.update_data(promocode=message.text)
        await message.answer(f"Промокод {promocode} успешно применен!", reply_markup=autokey({'Продолжить': 'OrderPreview', 'Отмена': 'start'}))
        await state.set_state(OrderState.OrderPreview)
    except:
        await message.answer(f"Промокод не существует, либо вы не можете его применить.", reply_markup=autokey({'Вернуться': 'OrderPreview'}))
        await state.set_state(OrderState.OrderPreview)

#Создаем заказ
@router.callback_query(F.data == "CreateOrder", OrderState.CreateOrder)
async def currency_choice(call: types.CallbackQuery, state: FSMContext):
    order_data = await state.get_data()

    order_id = int(f"{int(time.time())}{random.randint(10, 99)}")
    amount_input = order_data['amount_input']
    amount_output = order_data['amount_output']
    course = order_data['course']
    user_currency = order_data['user_currency']
    exchange_currency = order_data['exchange_currency']
    conversion_id = order_data['conversion_id']
    promocode = order_data.get('promocode', None)

    user = (await DjangoRepo.filter(User, telegram_id=call.message.chat.id))[0]
    order = await DjangoRepo.create(Order, {
        'user': user,
        'contact': user.contact,
        'order_id': order_id,
        'status': (await DjangoRepo.filter(OrderStatus, name="Создан"))[0],
        'type': (await DjangoRepo.filter(OrderType, name="Обмен"))[0],
        'currency': (await DjangoRepo.filter(Conversion, id=conversion_id))[0],
        'amount': amount_input,
        'amount_output': amount_output,
        'exchange_rate': course,
    })

    if promocode:
        promocode_usage = await DjangoRepo.create(PromocodeUsage, {
            'promocode': (await DjangoRepo.filter(Promocode, code=promocode))[0],
            'user': user,
            'order': order,
        })

    await call.message.edit_text(
        f"<b>Заказ №<code>{order_id}</code></b>\n" \
        f"<b>📝 Статус:</b> Создан\n" \
        f"<b>📦 Тип заказа:</b> Обмен\n" \
        f"<b>💰 Сумма:</b> { round(amount_input, 0) } {user_currency}\n" \
        f"<b>🔄 К получению:</b> { round(amount_output, 0) } {exchange_currency}\n" \
        f"<b>📊 Курс обмена:</b> {course}\n" \
        f"<b>🎟️ Промокод:</b> {promocode if promocode else "Нет"}\n"
    )
    await call.message.answer("Спасибо за заказ!", reply_markup=autokey({'Профиль': 'Profile', 'Меню': 'start'}))
    await state.clear()