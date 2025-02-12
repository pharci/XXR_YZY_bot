from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from .handlers.callbacks.training import router as router_training
from .handlers.commands.start import router as router_start
from .handlers.callbacks.exchange import router as router_exchange
from .handlers.callbacks.profile import router as router_profile

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(router_training)
dp.include_router(router_start)
dp.include_router(router_exchange)
dp.include_router(router_profile)