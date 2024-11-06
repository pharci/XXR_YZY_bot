from aiogram import Router, types
from aiogram.filters import Command
from app.bot.keyboards.keyboards import autokey
from aiogram import F, Router
from app.crud.user import get_or_create_user
from app.schemas.user import UserCreate
router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    user_data = UserCreate(user_id=message.from_user.id, username=message.from_user.username)
    user = await get_or_create_user(user_data)
    await message.delete()
    await message.answer(
        f"Добро пожаловать, {user.username}! Я ваш бот.", 
        reply_markup=autokey({'Обмен валюты': 'Exchange', 'Обучение': 'Training', 'Другое': 'Other', 'Профиль': 'Profile'})
        )

@router.callback_query(F.data == "start")
async def start(call: types.CallbackQuery):
    user = await add_or_get_user(call.message.chat.username, call.message.chat.id)
    user_data = UserCreate(user_id=call.message.chat.id, username=message.from_user.username,)
    user = await get_or_create_user(user_data)
    await call.message.edit_text(
        f"Привет {user.username}! Рад видеть!", 
        reply_markup=autokey({'Обмен валюты': 'Exchange', 'Обучение': 'Training', 'Другое': 'Other', 'Профиль': 'Profile'})
        )