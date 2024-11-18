from app.bot.bot import bot
from fastapi import FastAPI
from app.db.db import init_db_fastapi
from app.api.endpoints import user, bot_rout, auth
from app.core.config import settings
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.middlewares.auth import AuthMiddleware
import os
from app.db.models.user import User
from fastapi.middleware.cors import CORSMiddleware
from app.middlewares.cache import CacheControlMiddleware

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CacheControlMiddleware)
# app.add_middleware(AuthMiddleware)

app.include_router(user.router)
app.include_router(bot_rout.router)
app.include_router(auth.router)

app.mount(
    "/static", 
    StaticFiles(directory=os.path.join("app", "admin_panel", "static")), 
    name="static"
)

init_db_fastapi(app)

@app.on_event("startup")
async def startup_event():
    print("Установка вебхука.")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(f"{settings.WEBHOOK_URL}/webhook")

    first_user = await User.first()

    if first_user:
        first_user.is_superuser = True
        first_user.is_staff = True
        await first_user.save()
        print(f"Пользователь {first_user.username} теперь суперпользователь!")
    else:
        print("Первый пользователь не найден.")

@app.on_event("shutdown")
async def shutdown_event():
    await bot.delete_webhook(drop_pending_updates=True)