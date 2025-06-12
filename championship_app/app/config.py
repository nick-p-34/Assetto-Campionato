import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    AC_ROOT_PATH = os.getenv("AC_ROOT_PATH", "..").replace("\\", "/")
    DB_PATH = os.getenv("DB_PATH", "db/championship.db")
    PORT = int(os.getenv("PORT", 8000))

settings = Settings()