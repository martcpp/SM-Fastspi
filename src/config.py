ACCESS_TOKEN_EXPIRE_MINUTES = 30
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file if present

SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "277e57f3c135461b3a79765a426ebe6b6271a5cba502bd80e3909e9eb3e2ab94"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
