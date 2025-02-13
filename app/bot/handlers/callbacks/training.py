from aiogram import Router, types
from app.bot.keyboards import *
from aiogram import F, Router
from app.bot.keyboards.keyboards import autokey
from admin_app.bot.models import Bot, Study
from app.repository import DjangoRepo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()

class TrainingState(StatesGroup):
    ChooseRate = State()
    PreviewTrainingOrder = State()

@router.callback_query(F.data == "Training")
async def start(call: types.CallbackQuery, state: FSMContext):
    text = (await DjangoRepo.filter(Bot, message_id=2))[0].text
    buttons = await DjangoRepo.filter(Study, is_active=True)
    builder = InlineKeyboardBuilder()
    for i in buttons:
        builder.button(
            text=f"{i.name} - {i.amount} ₽", callback_data=f"{i.id}"
        )
    builder.button(text="Назад", callback_data="start")
    builder.adjust(1)
    await state.set_state(TrainingState.ChooseRate)
    return await call.message.edit_text(text, disable_web_page_preview=True, reply_markup=builder.as_markup())


@router.callback_query(F.data.func(lambda data: data.isdigit()), TrainingState.ChooseRate)
async def start(call: types.CallbackQuery, state: FSMContext):
    text = (await DjangoRepo.filter(Study, id=call.data))[0].text

    await state.set_state(TrainingState.PreviewTrainingOrder)
    return await call.message.edit_text(text, reply_markup=autokey({'Начать учиться': 'PreviewTrainingOrder', 'Назад': 'Training'}))



@router.callback_query(F.data == "PreviewTrainingOrder", TrainingState.PreviewTrainingOrder)
async def start(call: types.CallbackQuery, state: FSMContext):

    return await call.message.edit_text(
        "Предпросмотр заказа: ", 
        reply_markup=autokey({'Оформить заказ': 'CreateTrainingOrder', 'У меня есть промокод': 'promocode', 'Отменить заказ': 'start'})
    )