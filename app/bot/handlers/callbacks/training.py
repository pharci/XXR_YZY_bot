from aiogram import Router, types
from app.bot.keyboards import *
from aiogram import F, Router

router = Router()

@router.callback_query(F.data == "Training")
async def start(call: types.CallbackQuery):
    await call.message.edit_text("Обучение", reply_markup=autokey({'Назад': 'start'}))