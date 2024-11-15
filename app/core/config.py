from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    DATABASE_URL: str
    WEBHOOK_URL: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()


TORTOISE_ORM = {
    "connections": {
        "default": settings.DATABASE_URL
    },
    "apps": {
        "models": {
            "models": ["app.db.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}