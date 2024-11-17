import logging
from datetime import datetime
from typing import List, Optional

from pydantic import parse_obj_as
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, exists, and_
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import count

from resource_access.db_models.user_models import UserDB, UserPasswordResetTokenDB, UserActivityStats, UserDeviceDB
from schemas.user_schemas import (
    User, UserPasswordResetToken, UserActivityStatsSchema, UserDevice,
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

        except IntegrityError as error:
            logger.error(
                f"Error while updating User. Details: {error.orig.args}"
            )
            await self._session.rollback()
            await self.__integrity_error_handler(error, user_new_data)

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

    async def set_user_login_otp(
            self,
            user_id: int,
            otp: Optional[str] = None,
            otp_created_at: Optional[datetime] = None
    ) -> None:
        try:
            await self._session.execute(
                update(UserDB)
                .where(UserDB.id == user_id)
                .values(
                    login_otp=otp,
                    login_otp_created_at=otp_created_at
                )
            )
            await self._session.commit()
        except IntegrityError as error:
            logger.error(
                f"Error while updating User Login OTP. Details: {error.orig.args}"
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
        stats_db = UserActivityStats(
            user_id=user_stats.user_id,
            activity_type=user_stats.activity_type,
            action_date=user_stats.action_date,
        )
        self._session.add(stats_db)
        try:
            await self._session.commit()
            await self._session.refresh(stats_db)
            return UserActivityStatsSchema.model_validate(stats_db)
        except IntegrityError as error:
            logger.error(
                f"Error while creating User Activity Stats. Details: {error.orig.args}"
            )
            await self._session.rollback()
            await self.__integrity_error_handler(error, user_stats)

    async def get(
            self,
            *,
            user_email: Optional[str] = None,
            time_range: str = None,
            skip: int = 0,
            limit: int = 10,
    ) -> List[UserActivityStatsSchema]:
        where_args = []
        if user_email:
            where_args.append(UserDB.email == user_email)
        if time_range:
            pass

        stmt = (
            select(UserActivityStats)
            .join(
                UserDB,
                and_(
                    UserDB.id == UserActivityStats.user_id,
                ),
            )
            .where(*where_args)
            .limit(limit)
            .offset(skip)
            .order_by(UserActivityStats.action_date.desc())
        )
        query = await self._session.execute(stmt)
        return parse_obj_as(List[UserActivityStatsSchema], query.scalars().all())

    async def get_count(self, user_email: Optional[str] = None, time_range: Optional[str] = None) -> int:
        where_args = []
        if user_email:
            where_args.append(UserDB.email == user_email)
        if time_range:
            pass
        stmt = (
            select(count(UserActivityStats.id))
            .join(
                UserDB,
                and_(
                    UserDB.id == UserActivityStats.user_id,
                ),
            )
            .where(*where_args)
        )
        query = await self._session.execute(stmt)
        return query.scalar()

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


class UserDeviceRepository:
    def __init__(self, db_session: Session):
        self._session = db_session

    async def create_user_device(self, device: UserDevice) -> UserDevice:
        device_db = UserDeviceDB(**device.model_dump(exclude={'id'}))
        self._session.add(device_db)
        try:
            await self._session.commit()
            await self._session.refresh(device_db)
            return UserDevice.model_validate(device_db)
        except IntegrityError as error:
            logger.error(
                f"Error while creating User Device. Details: {error.orig.args}"
            )
            await self._session.rollback()
            await self.__integrity_error_handler(error, device)

    async def does_user_device_exist(self, user_id: int, device_id: str) -> bool:
        stmt = select(
            exists(
                select(UserDeviceDB).where(
                    UserDeviceDB.is_deleted.is_(False),
                    UserDeviceDB.user_id == user_id,
                    UserDeviceDB.device_id == device_id
                )
            )
        )
        query = await self._session.execute(stmt)
        return query.scalar()

    async def __integrity_error_handler(self, error, user=None) -> None:
        if error.orig.args[0] == 1062:  # MySQL unique constraint violation
            if "device_id" in error.orig.args[1]:
                raise AlreadyExistsException(
                    f"UserDevice already exists."
                )
            raise AlreadyExistsException(
                f"{error}"
            )

        raise AlreadyExistsException(
            f"{error}"
        )
