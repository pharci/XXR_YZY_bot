from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from typing import Optional
from aiogram.filters.callback_data import CallbackData

def autokey(dictkeys, rows=1):
    builder = InlineKeyboardBuilder()

    for key, value in dictkeys.items():
        builder.button(
            text=key, callback_data=str(value)
        )

    builder.adjust(rows)

    return builder.as_markup()