from aiogram import Bot, Dispatcher
from bot.config import settings
from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token=settings.telegram_token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)