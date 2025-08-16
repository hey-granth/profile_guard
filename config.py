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

    # Clerk
    CLERK_PUBLISHABLE_KEY: str = getenv("CLERK_PUBLISHABLE_KEY")
    CLERK_SECRET_KEY: str = getenv("CLERK_SECRET_KEY")
