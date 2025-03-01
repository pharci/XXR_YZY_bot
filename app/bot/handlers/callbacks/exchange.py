from aiogram import Router, types
from aiogram.filters import Filter
from .utils import createOrder, checkPromocode
from app.bot.keyboards import *
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.bot.keyboards.keyboards import autokey
from decimal import Decimal
from admin_app.orders.models import Conversion, Promocode, OrderTypeEnum
from admin_app.accounts.models import User
from asgiref.sync import sync_to_async
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
    return await call.message.edit_text("🔄Выберите валютную пару для обмена: ", reply_markup=builder.as_markup())

    

#Сохраняем валютную пару и спрашиваем в чем будет ввод
@router.callback_query(СonversionIdFilter(), OrderState.ChoosingInput)
async def currency_input(call: types.CallbackQuery, state: FSMContext):
    conversion = (await DjangoRepo.filter(Conversion, id=call.data))[0]

    await state.update_data(conversion_id=call.data)

    await call.message.edit_text(
        f"Выбранная валютная пара: {conversion.user_currency} -> {conversion.exchange_currency}\n\n" \
        "В чем вы хотите ввести сумму?",
        reply_markup=autokey({f'{conversion.user_currency}': f'{conversion.user_currency}',
                            f'{conversion.exchange_currency}': f'{conversion.exchange_currency}', 
                            'Отмена': 'start'})
        )
    await state.set_state(OrderState.input)

#Сохраняем вылюту ввода и просим ввести число
@router.callback_query(OrderState.input)
async def currency_input(call: types.CallbackQuery, state: FSMContext):
    order_data = await state.get_data()
    conversion = (await DjangoRepo.filter(Conversion, id=order_data["conversion_id"]))[0]

    await state.update_data(input_currency=call.data)

    await call.message.edit_text(
        f"<b>Зависимость курса от количества:</b>\n" \
        f"{await grade_text(conversion)}\n\n" \
        f"Введите сумму в {call.data}:",
        reply_markup=autokey({'Перейти к обучению': 'go_to_training', 'Отмена': 'start'})
        )

    await state.set_state(OrderState.receiving)


#Принимаем введеное число
@router.message(OrderState.receiving)
async def receiving_amount(message: types.Message, state: FSMContext): 
    order_data = await state.get_data()
    conversion = (await DjangoRepo.filter(Conversion, id=order_data["conversion_id"]))[0]
    graduations = conversion.grades

    minimum = int(min(graduations, key=graduations.get))
    minimum_second = round(minimum * conversion.course, 2)
    amount = message.text.strip().replace(" ", "")

    if re.fullmatch(r"-?\d+([.,]\d+)?", amount):
        amount = round(Decimal(amount.replace(",", ".")), 2)

        amout_for_check = amount
        if order_data["input_currency"] == conversion.user_currency:
            amout_for_check = round(amount / conversion.course, 2)

        if minimum <= amout_for_check <= Decimal(100000.00):
            await state.update_data(amount=amount)
            await message.answer(
                f"Вы ввели {amount}{order_data["input_currency"]}", 
                reply_markup=autokey({'Продолжить': 'OrderPreview', 'Отмена': 'start'})
                )
            await state.set_state(OrderState.OrderPreview)
        else:
            await message.answer(
                f"Минимум: {minimum}{conversion.exchange_currency} | {minimum_second}{conversion.user_currency}\n"
                f"Максимум: {100000}{conversion.exchange_currency} | {round(100000 * conversion.course, 2)}{conversion.user_currency}",  
                reply_markup=autokey({'Отмена': 'start'})
            )
    else:
        await message.answer(f"Неккоректный ввод. ", reply_markup=autokey({'Отмена': 'start'}))


async def grade_text(conversion):
    grade_text = []
    for key, value in conversion.grades.items():
        adjustment_course = round(conversion.course - Decimal(value), 2)
        grade_text.append(f"<b>От {key} {conversion.exchange_currency}  — </b> {adjustment_course}")
    grade_text.append(f"\n<i>Если пройти обучение, вы сможете обменивать самостоятельно по курсу <b>{conversion.clean_course}</b></i>.")
    return "\n".join(grade_text)


async def calculate(input_currency, conversion, amount, discount=0):
    matching_graduation = None
    grades = conversion.grades
    
    for key, value in grades.items():
        adjustment_course = round(conversion.course - Decimal(value), 2)

        if input_currency != conversion.user_currency:
            if Decimal(key) <= amount:
                matching_graduation = key
        else:
            if Decimal(key) <= round(amount / adjustment_course, 2):
                matching_graduation = key
    
    if not matching_graduation:
        return None, None, None, ""
    
    final_course = round(conversion.course - Decimal(grades[f"{matching_graduation}"]) - discount, 2)
    clean_course = conversion.clean_course
    
    if input_currency != conversion.user_currency:
        input_value = round(amount * final_course, 2)
        output_value = amount
    else:
        input_value = amount
        output_value = round(amount / final_course, 2)

    return input_value, output_value, final_course, clean_course

#Предпросмотр заказа
@router.callback_query(F.data == "OrderPreview", OrderState.OrderPreview)
@router.callback_query(F.data == "OrderPreview", OrderState.InputPromocode)
async def currency_choice(call: types.CallbackQuery, state: FSMContext):
    
    order_data = await state.get_data()
    conversion = (await DjangoRepo.filter(Conversion, id=order_data["conversion_id"]))[0]
    
    code = order_data.get('code', None)
    discount = 0
    if code:
        discount = (await DjangoRepo.filter(Promocode, code=code))[0].discount

    input, output, course, clean_course = await calculate(order_data['input_currency'], conversion, order_data["amount"], discount)

    await state.update_data(amount_input=input)
    await state.update_data(amount_output=output)
    await state.update_data(course=course)
    await state.update_data(clean_course=clean_course)

    text = f"<b>Предварительный просмотр:</b> \n\n" \
           f"<b>Тип заказа:</b> Обмен \n" \
           f"<b>Вы отдаете:</b> { round(input, 0) } {conversion.user_currency}\n" \
           f"<b>Вы получаете:</b> { round(output, 0) } {conversion.exchange_currency}\n" \
           f"<b>По курсу:</b> {course} { f"<s>{course + discount}</s>" if code else ""}\n" \
           f"<b>Промокод:</b> {f"{code} (-{discount})" if code else "Нет"} \n\n\n" \
           f"<b>Зависимость курса от количества:</b>\n" \
           f"{await grade_text(conversion)}"
    
    await call.message.edit_text(text, reply_markup=autokey({'Ввести промокод': 'code', 'Оформить заказ': 'CreateOrder', 'Отмена': 'start'}))
    await state.set_state(OrderState.CreateOrder)


#Просим ввести промокод
@router.callback_query(F.data == "code", OrderState.CreateOrder)
async def currency_choice(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите промокод:", reply_markup=autokey({'Назад': 'OrderPreview'}))
    await state.set_state(OrderState.InputPromocode)

#Принимаем промокод
@router.message(OrderState.InputPromocode)
async def receiving_amount(message: types.Message, state: FSMContext): 
    order_data = await state.get_data()

    user = (await DjangoRepo.filter(User, telegram_id=message.chat.id))[0]
    code = message.text
    order_type = OrderTypeEnum.EXCHANGE.value[0]

    response = await checkPromocode(
        message=message, 
        user=user, 
        order_type=order_type, 
        conversion_id=order_data["conversion_id"]
    )

    if response:
        await state.update_data(code=code)

    await state.set_state(OrderState.OrderPreview)


#Создаем заказ
@router.callback_query(F.data == "CreateOrder", OrderState.CreateOrder)
async def currency_choice(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(type=OrderTypeEnum.EXCHANGE.value[0])

    order_data = await state.get_data()

    await createOrder(call, order_data)

    await state.clear()