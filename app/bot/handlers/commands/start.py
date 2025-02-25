from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from app.bot.keyboards.keyboards import autokey
from aiogram import F, Router
from admin_app.accounts.models import User
from admin_app.bot.models import Bot
from app.bot.bot import bot
import os
from app.repository import DjangoRepo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

router = Router()

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    user = await DjangoRepo.filter(User, telegram_id=message.from_user.id)
    if not user:
        user = await DjangoRepo.create(User, {
            "telegram_id": message.from_user.id, 
            "username": message.chat.username if message.chat.username else message.from_user.id,
            "first_name": message.chat.first_name
        })

    message_bot = await DjangoRepo.filter(Bot, message_id=1)
    await state.clear()
    await message.answer(
        message_bot[0].text if message_bot else "Меню",
        disable_web_page_preview=True,
        reply_markup=autokey({'Обмен валюты': 'Exchange', 
                              'Самовыкуп': 'Selfpay', 
                              'Обучение': 'Training', 
                              'Профиль': 'Profile', 
                              'Помощь': 'help'})
    )

@router.callback_query(F.data == "start")
async def start(call: types.CallbackQuery, state: FSMContext):

    message_bot = await DjangoRepo.filter(Bot, message_id=1)

    await state.clear()
    await call.message.edit_text(
        message_bot[0].text if message_bot else "Меню", 
        disable_web_page_preview=True,
        reply_markup=autokey({'Обмен валюты': 'Exchange', 
                              'Самовыкуп': 'Selfpay', 
                              'Обучение': 'Training', 
                              'Профиль': 'Profile', 
                              'Помощь': 'help'})
        )
    
@router.callback_query(F.data == "help")
async def start(call: types.CallbackQuery):

    message_bot = await DjangoRepo.filter(Bot, message_id=3)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Основной канал", url="https://t.me/XXR_YZY_Changer"))
    builder.row(InlineKeyboardButton(text="Отзывы", url="https://t.me/XXR_YZY_Response"))
    builder.row(
        InlineKeyboardButton(text="Менеджер №1", url="https://t.me/Manager_XXR"),
        InlineKeyboardButton(text="Менеджер №2", url="https://t.me/Manager_YZY")
                )
    builder.row(InlineKeyboardButton(text="Разработчик бота", url="https://t.me/pharc1"))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="start"))

    await call.message.edit_text(
        message_bot[0].text if message_bot else "Помощь", 
        disable_web_page_preview=True,
        reply_markup=builder.as_markup(),
        )