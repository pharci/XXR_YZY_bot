from aiogram import Router, types
from aiogram.filters import Command
from admin.api import *
from bot.keyboards import *
from aiogram import F, Router

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    user = await add_or_get_user(message.from_user.username, message.from_user.id)
    await message.delete()
    await message.answer(
        f"Добро пожаловать, {user.username}! Я ваш бот.", 
        reply_markup=autokey({'Обмен валюты': 'Exchange', 'Обучение': 'Training', 'Другое': 'Other', 'Профиль': 'Profile'})
        )

@router.callback_query(F.data == "start")
async def start(call: types.CallbackQuery):
    user = await add_or_get_user(call.message.chat.username, call.message.chat.id)
    await call.message.edit_text(
        f"Привет {user.username}! Рад видеть!", 
        reply_markup=autokey({'Обмен валюты': 'Exchange', 'Обучение': 'Training', 'Другое': 'Other', 'Профиль': 'Profile'})
        )