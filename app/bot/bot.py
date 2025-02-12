from aiogram import Bot
from app.config import settings
import os
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_app.settings')
django.setup()



bot = Bot(
    token=settings.TELEGRAM_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    ))

