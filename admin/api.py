from fastapi import FastAPI
from .models import *
from .db import init_db, close_db
from pydantic import BaseModel
import random


class SysdataCreate(BaseModel):
    currency: str
    exchange_currency: str
    exchange_rate: float

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

@app.get("/users")
async def read_users():
    users = await User.all()
    return users

@app.post("/sysdata/")
async def create_sysdata(sysdata: SysdataCreate):
    new_sysdata = await Sysdata.create(
        currency=sysdata.currency,
        exchange_currency=sysdata.exchange_currency,
        exchange_rate=sysdata.exchange_rate
    )
    return {"id": new_sysdata.id, "currency": new_sysdata.currency}

@app.get("/sysdata/")
async def read_sysdata():
    all_sysdata = await Sysdata.all()
    return all_sysdata

async def get_currency_by_id(currency_id: int):
    try:
        currency_data = await Sysdata.get(id=currency_id)  # Получаем запись по ID
        return {
            "id": currency_data.id,
            "currency": currency_data.currency,
            "exchange_currency": currency_data.exchange_currency,
            "exchange_rate": str(currency_data.exchange_rate)  # Конвертируем Decimal в строку для JSON
        }
    except:
        return None 

async def add_or_get_user(username: str, user_id: int):
    user, created = await User.get_or_create(username=username, user_id=user_id)
    return user

async def get_all_currencies():
    currencies = await Sysdata.all()
    return list(currencies)

async def create_order(user_id: int, contact_method: str, currency: str, amount: float, exchange_currency: str, exchange_rate: float):
    order_id = random.randint(10000000, 99999999)
    while await Order.filter(order_id=order_id).exists():
        order_id = random.randint(10000000, 99999999)

    order = await Order.create(
        user=user_id,
        order_id=order_id,
        contact_method=contact_method,
        currency=currency,
        amount=amount,
        exchange_currency=exchange_currency,
        exchange_rate=exchange_rate
    )
    return order

async def get_last_5_orders(user: User):
    last_orders = await Order.filter(user=user).order_by('-id').limit(5)
    return last_orders