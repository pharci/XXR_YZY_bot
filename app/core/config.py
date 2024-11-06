from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    telegram_token: str
    DATABASE_URL: str
    WEBHOOK_URL: str

    class Config:
        env_file = ".env"

settings = Settings()