from app.bot.bot import bot
from fastapi import FastAPI
from app.core.db import init_db_fastapi
from app.api.endpoints import user, admin, bot_rout
from app.core.config import settings

app = FastAPI(debug=True)

app.include_router(user.router)
app.include_router(admin.router)
app.include_router(bot_rout.router)

init_db_fastapi(app)

@app.on_event("startup")
async def startup_event():
    print("Установка вебхука.")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(f"{settings.WEBHOOK_URL}/webhook")

@app.on_event("shutdown")
async def shutdown_event():
    await bot.delete_webhook(drop_pending_updates=True)