from dotenv import load_dotenv
from os import getenv


load_dotenv()


class Config:
    SECRET_KEY: str = getenv("SECRET_KEY")
    DEBUG: bool = getenv("DEBUG", "False") == "True"
