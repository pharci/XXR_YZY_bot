from fastapi import APIRouter, HTTPException
from app.schemas.user import UserGet
from app.schemas.order import OrderGet
from app.crud.user import get_user, get_all_users
from app.crud.order import get_all_orders, get_order_by_id, get_all_user_orders
from typing import List

router = APIRouter()

@router.get("/users/", response_model=List[UserGet])
async def read_all_users():
    return await get_all_users()

@router.get("/users/{user_id}", response_model=UserGet)
async def read_user(user_id: int):
    return await get_user(user_id=user_id)

@router.get("/orders/", response_model=List[OrderGet])
async def read_orders():
    return await get_all_orders()

@router.get("/orders/{order_id}", response_model=OrderGet)
async def read_order_by_id(order_id: int):
    order = await get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

@router.get("/{user_id}/orders", response_model=List[OrderGet])
async def read_all_user_orders(user_id: int):
    user = await get_user(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    orders = await get_all_user_orders(user=user)
    return orders