from aiogram import Router, types
from app.bot.keyboards import *
from aiogram import F, Router
from datetime import timedelta
from app.bot.keyboards.keyboards import autokey
from admin_app.accounts.models import User
from app.repository import DjangoRepo
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton 
from aiogram.fsm.context import FSMContext

router = Router()

class ContactState(StatesGroup):
    setContact = State()
    
@router.callback_query(F.data == "Profile")
async def profile(call: types.CallbackQuery):
    user = await DjangoRepo.filter(User, telegram_id=call.message.chat.id)
    await call.message.edit_text(
        f"ID: {user[0].telegram_id}\n"
        f"username: @{user[0].username}\n"
        f"Телефон: {user[0].contact}\n"
        f"Дата регистрации: {(user[0].date_joined + timedelta(hours=3)).strftime("%d.%m.%Y %H:%M:%S")}", 
        reply_markup=autokey({'Последние 5 заказов': 'ShowOrders', 'Установить номер телефона': 'setContact', 'Назад': 'start'})
    )

@router.callback_query(F.data == "ShowOrders")
async def orders(call: types.CallbackQuery):
    user = await DjangoRepo.filter(User, telegram_id=call.message.chat.id)
    text = await DjangoRepo.call_model_method(user[0], "get_5_orders")
    await call.message.edit_text(
        text, reply_markup=autokey({'Назад': 'Profile', 'Меню': 'start'})
    )

@router.callback_query(F.data == "setContact")
async def setContact(call: types.CallbackQuery, state: FSMContext):
    kb_list = [[KeyboardButton(text='Поделиться контактом', request_contact=True)], [KeyboardButton(text='Отмена')]]
    await call.message.answer(
        "Нажмите кнопку ниже, чтобы отправить контакт.", 
        reply_markup=ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    )
    await state.set_state(ContactState.setContact)

@router.message(F.contact.is_not(None), ContactState.setContact)
async def inputContact(message: types.Message, state: FSMContext): 
    user = await DjangoRepo.filter(User, telegram_id=message.chat.id)
    await DjangoRepo.update(User, user[0].id, {"contact": message.contact.phone_number})

    sent_message = await message.answer("loading...", reply_markup=ReplyKeyboardRemove())
    await sent_message.delete()

    await message.answer(
            "Ваш контакт сохранен.", 
            reply_markup=autokey({'Профиль': 'Profile', 'Меню': 'start'})
        )
    await state.clear()

@router.message(F.contact.is_(None), ContactState.setContact)
async def contactNone(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':

        await message.delete()

        sent_message = await message.answer("loading...", reply_markup=ReplyKeyboardRemove())
        await sent_message.delete()

        await message.answer(
            "Контакт не сохранен.", 
            reply_markup=autokey({'Профиль': 'Profile', 'Меню': 'start'})
        )
        return await state.clear()
    return await message.answer("Возникла ошибка, попробуйте еще раз.")