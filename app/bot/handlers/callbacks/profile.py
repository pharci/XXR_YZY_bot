from aiogram import Router, types
from app.bot.keyboards import *
from aiogram import F, Router
from datetime import timedelta
from app.bot.keyboards.keyboards import autokey
from admin_app.accounts.models import User
from app.repository import DjangoRepo
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

router = Router()

class ContactState(StatesGroup):
    setContact = State()
    
@router.callback_query(F.data == "Profile")
async def profile(call: types.CallbackQuery):
    user = await DjangoRepo.filter(User, telegram_id=call.message.chat.id)
    await call.message.edit_text(
        f"📌 <b>Профиль</b>\n\n" \
        f"👤 <b>Имя пользователя:</b> @{user[0].username}\n\n" \
        f"📅 <b>Дата регистрации:</b> <code>{(user[0].date_joined + timedelta(hours=3)).strftime("%d.%m.%Y")}</code>\n\n" \
        f"📞 <b>Телефон:</b> <code>+{user[0].contact}</code>\n\n",
        reply_markup=autokey({'Мои заказы': 'orders_page_1', 'Установить номер телефона': 'setContact', 'Назад': 'start'})
    )


def get_pagination_keyboard(page: int, total_pages: int):
    builder = InlineKeyboardBuilder()

    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton(
            text="⏪", callback_data=f"orders_page_{page-1}"
        ))
    buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="none"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="⏩", callback_data=f"orders_page_{page+1}"))
    builder.row(*buttons)

    builder.row(InlineKeyboardButton(text="Профиль", callback_data="Profile"))
    builder.row(InlineKeyboardButton(text="Меню", callback_data="start"))

    return builder.as_markup()

@router.callback_query(F.data.startswith('orders_page_'))
async def orders(call: types.CallbackQuery):
    user = await DjangoRepo.filter(User, telegram_id=call.message.chat.id)
    orders = await DjangoRepo.call_model_method(user[0], "get_orders")
    if not orders:
        await call.message.edit_text(
            "У вас пока нет заказов, но надеюсь они скоро появятся ♡", 
            reply_markup=autokey({'Назад': 'Profile'})
        )

    page = int(call.data.split("_")[2])
    ITEMS_PER_PAGE = 3

    total_pages = (len(orders) - 1) // ITEMS_PER_PAGE + 1
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE

    keyboard = get_pagination_keyboard(page, total_pages)
    await call.message.edit_text(
        "<b>📃 Ваши заказы:</b>\n\n" + "\n<i>━━━━━━━━━━━━━━━━━━━━━━</i>\n\n".join(orders[start_idx:end_idx]), 
        reply_markup=keyboard
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