from app.db.models.user import User
from app.schemas.user import UserCreate
from typing import List

async def get_or_create_user(user_data: UserCreate) -> User:
    user, created = await User.get_or_create(
        user_id=user_data.user_id, 
        username=user_data.username,
        first_name=user_data.first_name
    )
    return user

async def get_user(user_id: int) -> User:
    user = await User.get(user_id=user_id)
    return user

async def get_all_users() -> List[User]:
    users = await User.all()
    return list(users)

async def update_user(user_id: int, username: str = None, description: str = None):
    user = await get_user(user_id)
    if user:
        update_fields = []
        if username:
            user.username = username
            update_fields.append('username')
        if description:
            user.description = description
            update_fields.append('description')

        await user.save(update_fields=update_fields)
        return user
    return None

async def delete_user(user_id: int):
    user = await get_user(user_id)
    if user:
        await user.delete()
        return True
    return False