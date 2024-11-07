from aiogram import Router, types
from app.bot.keyboards import *
from aiogram import F, Router
from app.bot.keyboards.keyboards import autokey

router = Router()

@router.callback_query(F.data == "Other")
async def start(call: types.CallbackQuery):
    await call.message.edit_text("Другое", reply_markup=autokey({'Назад': 'start'}))