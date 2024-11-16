import logging
from typing import List

from pydantic import parse_obj_as
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update
from sqlalchemy.orm import Session


from resource_access.db_models.user_models import UserDB, UserPasswordResetTokenDB, UserActivityStats
from schemas.enums.user_enums import UserActivityTypeEnum
from schemas.user_schemas import (
    User, UserPasswordResetToken, UserActivityStatsSchema,
)
from utils.exceptions import NotFoundException, AlreadyExistsException

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db_session: Session):
        self._session = db_session

    async def create_user(self, user: User) -> User:
        user_db = UserDB(**user.model_dump(exclude={'id'}))
        self._session.add(user_db)
        try:
            await self._session.commit()
            await self._session.refresh(user_db)
            return User.model_validate(user_db)
        except IntegrityError as error:
            logger.error(
                f"Error while creating User. Details: {error.orig.args}"
            )
            await self._session.rollback()
            await self.__integrity_error_handler(error, user)

    async def update_user(self, user_new_data: User, user_id: int) -> None:
        try:
            query = await self._session.execute(
                update(UserDB)
                .where(UserDB.id == user_id)
                .values(**user_new_data.model_dump(
                    exclude_unset=True,
                    exclude={"id", "hashed_password", "email", "role"},
                ))
            )
            await self._session.commit()
            user_db = query.one()
            return User.model_validate(user_db)
        except IntegrityError as error:
            logger.error(
                f"Error while updating User. Details: {error.orig.args}"
            )
            await self._session.rollback()
            await self.__integrity_error_handler(error, user)

    async def update_user_password(self, user_id: int, token: str, new_hashed_password: str) -> None:
        try:
            update_user_query = await self._session.execute(
                update(UserDB)
                .where(UserDB.id == user_id)
                .values(hashed_password=new_hashed_password)
            )
            await self._session.execute(
                update(UserPasswordResetTokenDB)
                .where(UserPasswordResetTokenDB.token == token)
                .values(is_deleted=True)
            )
            await self._session.commit()
        except IntegrityError as error:
            logger.error(
                f"Error while updating User. Details: {error.orig.args}"
            )
            await self._session.rollback()
            await self.__integrity_error_handler(error)

    async def get_user_by_email(self, email: str) -> User:
        query = await self._session.execute(
            select(UserDB).where(
                UserDB.email == email, UserDB.is_deleted.is_(False)
            )
        )
        user_db = query.scalar()
        if user_db:
            return User.model_validate(user_db)
        raise NotFoundException(f"User not found: {email}")

    async def get_user_by_id(self, user_id: int) -> User:
        query = await self._session.execute(
            select(UserDB).where(
                UserDB.id == user_id, UserDB.is_deleted.is_(False)
            )
        )
        user_db = query.scalar()
        if user_db:
            return User.model_validate(user_db)
        raise NotFoundException(f"Нет пользователя с id: {user_id}")

    async def create_password_reset_token(self, token: UserPasswordResetToken):
        token_db = UserPasswordResetTokenDB(
            user_id=token.user_id,
            token=token.token,
            expires_at=token.expires_at,
        )
        self._session.add(token_db)
        try:
            await self._session.commit()
            await self._session.refresh(token_db)
            return UserPasswordResetToken.model_validate(token_db)
        except IntegrityError as error:
            logger.error(
                f"Error while creating UserPasswordResetToken. Details: {error.orig.args}"
            )
            await self._session.rollback()
            await self.__integrity_error_handler(error, token)

    async def get_reset_password_token(self, token: str) -> UserPasswordResetToken:
        query = await self._session.execute(
            select(UserPasswordResetTokenDB).where(
                UserPasswordResetTokenDB.token == token, UserPasswordResetTokenDB.is_deleted.is_(False)
            )
        )
        token_db = query.scalar()
        if not token_db or not token_db.is_valid():
            raise NotFoundException(f"Token does not exist or has expired.")
        return UserPasswordResetToken.model_validate(token_db)

    async def __integrity_error_handler(self, error, user=None) -> None:
        if error.orig.args[0] == 1062:  # MySQL unique constraint violation
            if "email" in error.orig.args[1]:
                raise AlreadyExistsException(
                    f"User with the email '{user.email}' already exists."
                )
            if "phone" in error.orig.args[1]:
                raise AlreadyExistsException(
                    f"User with the phone '{user.phone}' already exists."
                )
            raise AlreadyExistsException(
                f"{error}"
            )

        raise AlreadyExistsException(
            f"{error}"
        )


class UserActivityStatsRepository:
    def __init__(self, db_session: Session):
        self._session = db_session

    async def create(self, user_stats: UserActivityStatsSchema) -> UserActivityStatsSchema:
        stats_db = UserActivityStats(**user_stats.model_dump(exclude={'id'}))
        self._session.add(stats_db)
        try:
            await self._session.commit()
            await self._session.refresh(stats_db)
            return User.model_validate(stats_db)
        except IntegrityError as error:
            logger.error(
                f"Error while creating User Activity Stats. Details: {error.orig.args}"
            )
            await self._session.rollback()
            await self.__integrity_error_handler(error, user_stats)

    async def get(self, user_id: id = None, time_range: str = None) -> List[UserActivityStatsSchema]:
        where_args = []
        if user_id:
            where_args.append(UserActivityStats.user_id == user_id)
        if time_range:
            pass

        stmt = (
            select(UserActivityStats)
            .where(*where_args)
            .order_by(UserActivityStats.action_date.desc())
        )
        query = await self._session.execute(stmt)
        return parse_obj_as(List[UserActivityStatsSchema], query.scalars().all())
