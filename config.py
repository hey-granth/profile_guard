from dotenv import load_dotenv
from os import getenv


load_dotenv()


class Config:
    SECRET_KEY: str = getenv("SECRET_KEY")
    DEBUG: bool = getenv("DEBUG", "False") == "True"

    # Database
    DB_NAME: str = getenv("DB_NAME", "dating_app")
    DB_USER: str = getenv("DB_USER", "postgres")
    DB_PASSWORD: str = getenv("DB_PASSWORD", "password")
    DB_HOST: str = getenv("DB_HOST", "localhost")
    DB_PORT: str = getenv("DB_PORT", "5432")

    # Google OAuth
    GOOGLE_CLIENT_ID: str = getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = getenv(
        "GOOGLE_REDIRECT_URI", "http://localhost:8000/accounts/google/callback/"
    )

    REDIS_URL: str = getenv("REDIS_URL", "redis://localhost:6379/0")
