from app.db.models.user import User
from app.schemas.user import UserCreate
from typing import List

async def get_or_create_user(user_data: UserCreate) -> User:
    user, created = await User.get_or_create(
        user_id=user_data.user_id, 
        username=user_data.username
    )
    return user

async def get_user(user_id: int) -> User:
    user = await User.get(user_id=user_id)
    return user

async def get_all_users() -> List[User]:
    users = await User.all()
    return list(users)