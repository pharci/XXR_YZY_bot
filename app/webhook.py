from fastapi import APIRouter, Request
from app.bot.bot import bot
from app.bot.dp import dp
from aiogram.types import Update

router = APIRouter()

@router.post("/webhook")
async def webhook(request: Request):
    try:
        request_data = await request.json()
        update = Update.model_validate(await request.json(), context={"bot": bot})
        await dp.feed_update(bot, update)

        return {"message": "Webhook received", "data": request_data}

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"error": str(e)}