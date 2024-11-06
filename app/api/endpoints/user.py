from fastapi import APIRouter
from app.schemas.user import UserGet
from app.crud.user import get_user
from typing import List

router = APIRouter()

@router.get("/users", response_model=List[UserGet])
async def get_users():
    users = await User.all()
    return users