from aiogram import Bot, Dispatcher
from app.core.config import settings
from aiogram.fsm.storage.memory import MemoryStorage
from .handlers.callbacks.training import router as r_tr
from .handlers.callbacks.other import router as r_ot
from .handlers.commands.start import router as r_st
from .handlers.callbacks.exchange import router as r_ex
from .handlers.callbacks.profile import router as r_pr

bot = Bot(token=settings.TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(r_tr)
dp.include_router(r_ot)
dp.include_router(r_st)
dp.include_router(r_ex)
dp.include_router(r_pr)
