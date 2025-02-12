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

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    photos = await bot.get_user_profile_photos(message.from_user.id)
    if photos.total_count > 0:
        photo = photos.photos[0][-1]
        file = await bot.get_file(photo.file_id)
        photo_path = os.path.join(os.path.join(os.getcwd(), "admin_app", "media", "avatars"), f"{message.chat.id}.png")
        await bot.download_file(file.file_path, photo_path)

    user = await DjangoRepo.filter(User, telegram_id=message.from_user.id)
    if not user:
        user = await DjangoRepo.create(User, {
            "telegram_id": message.from_user.id, 
            "username": message.chat.username if message.chat.username else message.from_user.id,
            "avatar": os.path.join("avatars", f"{message.chat.id}.png"),
            "first_name": message.chat.first_name
        })

    message_bot = await DjangoRepo.filter(Bot, message_id=1)
    await message.answer(
        message_bot[0].text,
        disable_web_page_preview=True,
        reply_markup=autokey({'Обмен валюты': 'Exchange', 'Обучение': 'Training', 'Профиль': 'Profile'})
    )


@router.callback_query(F.data == "start")
async def start(call: types.CallbackQuery, state: FSMContext):
    await state.clear()

    message_bot = await DjangoRepo.filter(Bot, message_id=1)

    await call.message.edit_text(
        message_bot[0].text, 
        disable_web_page_preview=True,
        reply_markup=autokey({'Обмен валюты': 'Exchange', 'Обучение': 'Training', 'Профиль': 'Profile'},
        ))