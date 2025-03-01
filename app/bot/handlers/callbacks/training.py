from aiogram import Router, types
from app.bot.keyboards import *
from aiogram import F, Router
from app.bot.keyboards.keyboards import autokey
from admin_app.bot.models import Bot, Tariff, Category
from app.repository import DjangoRepo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from admin_app.orders.models import Conversion, Promocode, OrderTypeEnum
from admin_app.accounts.models import User
from .utils import createOrder, checkPromocode
from .exchange import OrderState

router = Router()

class TrainingState(StatesGroup):
    Category = State()
    ChooseRate = State()
    OrderPreview = State()
    InputPromocode = State()
    CreateOrder = State()


@router.callback_query(OrderState.receiving, F.data == "go_to_training")
@router.callback_query(F.data == "Training")
async def start(call: types.CallbackQuery, state: FSMContext):

    await state.clear()

    user = await DjangoRepo.filter(User, telegram_id=call.message.chat.id)
    if not user[0].contact:
        return await call.message.edit_text(
            "Чтобы создать заказ, установите номер телефона в профиле.", 
            reply_markup=autokey({'Профиль': 'Profile', 'Отмена': 'start'})
        )

    text = (await DjangoRepo.filter(Bot, message_id=2))[0].text

    categories = await DjangoRepo.filter(Category, is_active=True)
    categories.sort(key=lambda x: x.order, reverse=True)

    builder = InlineKeyboardBuilder()
    for i in categories:
        builder.button(
            text=f"{i.name}", callback_data=f"Category_{i.id}"
        )
    builder.button(text="Назад", callback_data="start")
    builder.adjust(1)
    await state.set_state(TrainingState.Category)
    return await call.message.edit_text(text, disable_web_page_preview=True, reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("BackToCategory_"), TrainingState.OrderPreview)
@router.callback_query(F.data.startswith("Category_"), TrainingState.Category)
async def start(call: types.CallbackQuery, state: FSMContext):
    category_id = call.data.split("_")[1]
    category = (await DjangoRepo.filter(Category, id=category_id))[0]
    await state.update_data(category_id=category_id)

    tariffs = await DjangoRepo.filter(Tariff, category__id=category_id, is_active=True)
    tariffs.sort(key=lambda x: x.order, reverse=True)

    builder = InlineKeyboardBuilder()
    for i in tariffs:
        builder.button(
            text=f"{i.name} - {i.amount} ₽", callback_data=f"{i.id}"
        )
    builder.button(text="Назад", callback_data="Training")
    builder.adjust(1)


    await state.set_state(TrainingState.ChooseRate)
    return await call.message.edit_text(category.text, disable_web_page_preview=True, reply_markup=builder.as_markup())


@router.callback_query(F.data.func(lambda data: data.isdigit()), TrainingState.ChooseRate)
async def start(call: types.CallbackQuery, state: FSMContext):
    order_data = await state.get_data()

    text = (await DjangoRepo.filter(Tariff, id=call.data))[0].text

    await state.update_data(tariff_id=call.data)

    await state.set_state(TrainingState.OrderPreview)
    return await call.message.edit_text(
        text, 
        reply_markup=autokey({'Начать учиться': 'OrderPreview', 'Назад': f'BackToCategory_{order_data["category_id"]}'})
    )


@router.callback_query(F.data == "OrderPreview", TrainingState.OrderPreview)
@router.callback_query(F.data == "OrderPreview", TrainingState.InputPromocode)
async def currency_choice(call: types.CallbackQuery, state: FSMContext):
    
    order_data = await state.get_data()

    tariff = (await DjangoRepo.filter(Tariff, id=order_data.get('tariff_id', None)))[0]

    code = order_data.get('code', None)
    discount = 0
    if code:
        discount = (await DjangoRepo.filter(Promocode, code=code))[0].discount

    amount_input = tariff.amount - discount if code else tariff.amount
    await state.update_data(amount_input=amount_input)


    text = f"<b>Предварительный просмотр:</b> \n\n" \
           f"<b>Тип заказа:</b> Обучение \n" \
           f"<b>Тариф:</b> {tariff.name} \n" \
           f"<b>Цена:</b> {amount_input}₽\n" \
           f"<b>Промокод:</b> {f"{code} (-{discount}₽)" if code else "Нет"} \n\n\n" \
    
    await call.message.edit_text(text, reply_markup=autokey({'Ввести промокод': 'code', 'Оформить заказ': 'CreateOrder', 'Отмена': 'start'}))
    await state.set_state(TrainingState.CreateOrder)


#Просим ввести промокод
@router.callback_query(F.data == "code", TrainingState.CreateOrder)
async def currency_choice(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите промокод:", reply_markup=autokey({'Назад': 'OrderPreview'}))
    await state.set_state(TrainingState.InputPromocode)

#Принимаем промокод
@router.message(TrainingState.InputPromocode)
async def receiving_amount(message: types.Message, state: FSMContext): 
    user = (await DjangoRepo.filter(User, telegram_id=message.chat.id))[0]
    code = message.text
    order_type = OrderTypeEnum.STUDY.value[0]
    order_data = await state.get_data()

    response = await checkPromocode(
        message=message, 
        user=user, 
        order_type=order_type, 
        tariff_id=order_data['tariff_id'],
    )

    if response:
        await state.update_data(code=code)

    await state.set_state(TrainingState.OrderPreview)


#Создаем заказ
@router.callback_query(F.data == "CreateOrder", TrainingState.CreateOrder)
async def currency_choice(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(type=OrderTypeEnum.STUDY.value[0])

    order_data = await state.get_data()

    await createOrder(call, order_data)

    await state.clear()