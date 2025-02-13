from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from .handlers.callbacks.training import router as training
from .handlers.commands.start import router as start
from .handlers.callbacks.exchange import router as exchange
from .handlers.callbacks.profile import router as profile
from .handlers.callbacks.selfpay import router as selfpay

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(training)
dp.include_router(start)
dp.include_router(exchange)
dp.include_router(profile)
dp.include_router(selfpay)