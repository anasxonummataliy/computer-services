import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")

    EMAIL_HOST_USER: str = ""
    EMAIL_HOST_PASS: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
