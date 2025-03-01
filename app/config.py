from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    DATABASE_URL: str
    WEBHOOK_URL: str
    SECRET_KEY: str
    GROUP_ID: int

    DEBUG: bool
    ALLOWED_HOSTS: str
    CSRF_TRUSTED_ORIGINS: str

    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int

    class Config:
        env_file = ".env"

settings = Settings()