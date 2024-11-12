from aiogram import Router, types
from aiogram.filters import Command
from app.bot.keyboards.keyboards import autokey
from aiogram import F, Router
from app.crud.user import get_or_create_user, get_user
from app.schemas.user import UserCreate
router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    if message.from_user.username:
        username = message.from_user.username
    else:
        username = "Отсутствует"

    user_data = UserCreate(user_id=message.from_user.id, username=username, first_name=message.from_user.first_name)
    user = await get_or_create_user(user_data)
    
    await message.answer(
        f"Добро пожаловать, {user.first_name}! Я ваш бот.", 
        reply_markup=autokey({'Обмен валюты': 'Exchange', 'Обучение': 'Training', 'Другое': 'Other', 'Профиль': 'Profile'})
        )

@router.callback_query(F.data == "start")
async def start(call: types.CallbackQuery):
    user = await get_user(call.message.chat.id)
    await call.message.edit_text(
        f"Привет {user.first_name}! Рад видеть!", 
        reply_markup=autokey({'Обмен валюты': 'Exchange', 'Обучение': 'Training', 'Другое': 'Other', 'Профиль': 'Profile'})
        )