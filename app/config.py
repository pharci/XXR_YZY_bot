from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    DATABASE_URL: str
    WEBHOOK_URL: str
    SECRET_KEY: str
    GROUP_ID: int

    class Config:
        env_file = ".env"

settings = Settings()