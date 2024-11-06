from app.db.models.user import User
from app.schemas.user import UserCreate

async def get_or_create_user(user_data: UserCreate) -> User:
    user, created = await User.get_or_create(user_id=user_data.user_id, defaults=user_data.dict())
    return user

async def get_user(user_id: int) -> User:
    user = await User.get(id=user_id)
    return user