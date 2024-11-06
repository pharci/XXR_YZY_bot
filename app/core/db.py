from tortoise import Tortoise
from app.core.config import settings
from app.db.base import init_models
from tortoise.contrib.fastapi import register_tortoise

async def init_db():
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={'models': ['models']},
    )
    init_models()
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()


def init_db_fastapi(app):
    register_tortoise(
        app,
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.db.models"]},
        generate_schemas=True,  # автоматически создать схемы, если их нет
        add_exception_handlers=True,
    )