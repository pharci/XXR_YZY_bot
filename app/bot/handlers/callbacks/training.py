from aiogram import Router, types
from app.bot.keyboards import *
from aiogram import F, Router
from app.bot.keyboards.keyboards import autokey
from asgiref.sync import sync_to_async
from admin_app.bot.models import Bot

router = Router()

@router.callback_query(F.data == "Training")
async def start(call: types.CallbackQuery):

    message_from_db = await sync_to_async(Bot.objects.get)(message_id=2)

    await call.message.edit_text(message_from_db.text, disable_web_page_preview=True, reply_markup=autokey({'Назад': 'start'}))