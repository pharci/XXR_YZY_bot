from aiogram import Router, types
from admin.api import *
from ..keyboards import *
from aiogram import F, Router
from ..main import dp, bot

router = Router()

@dp.callback_query(F.data == "Training")
async def start(call: types.CallbackQuery):
    await call.message.edit_text("Обучение", reply_markup=autokey({'Назад': 'start'}))