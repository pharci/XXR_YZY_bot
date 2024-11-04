from .handlers.training import router as r_tr
from .handlers.other import router as r_ot
from .handlers.start import router as r_st
from .handlers.exchange import router as r_ex
from .handlers.profile import router as r_pr

from .main import bot, dp
from admin.db import init_db, close_db
import asyncio

async def main():
    await init_db()

    dp.include_router(r_tr)
    dp.include_router(r_ot)
    dp.include_router(r_st)
    dp.include_router(r_ex)
    dp.include_router(r_pr)

    await dp.start_polling(bot)