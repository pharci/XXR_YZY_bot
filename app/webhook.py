import logging
from fastapi import APIRouter, Request
from app.bot.bot import bot
from app.bot.dp import dp
from aiogram.types import Update
from app.config import settings

logger = logging.getLogger(__name__)
log_format = "%(asctime)s - %(levelname)s - %(message)s"
file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(log_format))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)

router = APIRouter()

@router.post(f"/{settings.TELEGRAM_TOKEN}/webhook")
async def webhook(request: Request):
    try:
        request_data = await request.json()
        update = Update.model_validate(request_data, context={"bot": bot})
        await dp.feed_update(bot, update)
        return {"message": "Webhook received", "data": request_data}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"error": str(e)}