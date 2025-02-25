from fastapi import FastAPI
from app.webhook import router
from app.config import settings
from fastapi.staticfiles import StaticFiles
import os
from django.core.asgi import get_asgi_application
from contextlib import asynccontextmanager
import django
from app.bot.bot import bot

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_app.settings')
django.setup()
application = get_asgi_application()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(f"{settings.WEBHOOK_URL}/{settings.TELEGRAM_TOKEN}/webhook")
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/admin", application)

app.mount(
    "/static", 
    StaticFiles(directory=os.path.join(os.getcwd(), "admin_app", "static")), 
    name="static"
)

app.include_router(router)