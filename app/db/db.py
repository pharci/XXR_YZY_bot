from tortoise import Tortoise
from app.core.config import settings
from tortoise.contrib.fastapi import register_tortoise
from app.core.config import TORTOISE_ORM

async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()

def init_db_fastapi(app):
    register_tortoise(
        app,
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.db.models"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )