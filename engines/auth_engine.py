import random
import string

from schemas.user_schemas import User
from passlib.context import CryptContext

from utils.exceptions import AuthenticationError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationEngine:
    @staticmethod
    async def check_password(user: User, password: str):
        valid = False
        if user.hashed_password:
            valid = pwd_context.verify(password, user.hashed_password)
        if not valid:
            raise AuthenticationError(message="Wrong password")

    @staticmethod
    async def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    async def create_random_password() -> str:
        characters = string.ascii_letters + string.digits
        password = "".join(random.choice(characters) for i in range(10))
        return password
