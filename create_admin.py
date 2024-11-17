import asyncio
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from engines.auth_engine import AuthenticationEngine
from resource_access.db_models.user_models import UserDB
from resource_access.db_session import AsyncSessionLocal
from schemas.enums.user_enums import UserRoleEnum

logger = logging.getLogger(__name__)


def get_user_input():
    email = input("email: ")
    password = input("password: ")
    return email, password


async def create_admin(session: Session, email: str, hashed_password: str):
    db_user = UserDB(
        email=email,
        hashed_password=hashed_password,
        role=UserRoleEnum.admin,
    )
    session.add(db_user)
    try:
        await session.commit()
        print("Admin is created")
    except IntegrityError as e:
        logger.error(f"Error while creating Admin. Details: {e.orig.args}")
        await session.rollback()
        if e.orig.args[0] == 1062:  # MySQL unique constraint violation
            if "email" in e.orig.args[0]:
                print(f"User with email {email} already exists!")


async def create_admin_with_session():
    email, password = get_user_input()
    hashed_password = await AuthenticationEngine.get_password_hash(password)
    async with AsyncSessionLocal() as session:
        await create_admin(session, email, hashed_password)


if __name__ == "__main__":
    asyncio.run(create_admin_with_session())
