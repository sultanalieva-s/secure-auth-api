from datetime import datetime, UTC, timedelta
from typing import Dict, List

from sqlalchemy.orm import Session

from core import jwt_tokens
from core.config import settings
from core.jwt_tokens import create_access_token, create_refresh_token
from engines.auth_engine import AuthenticationEngine
from engines.email_engine import EmailEngine
from resource_access import db_session
from resource_access.repositories.user_repos import UserRepository, UserActivityStatsRepository, UserDeviceRepository
from schemas.enums.user_enums import UserRoleEnum, UserActivityTypeEnum
from schemas.user_schemas import UserSignUp, User, UserUpdate, TokenPayload, UserPasswordResetToken, \
    UserActivityStatsSchema, UserDevice
from jose import jwt
import secrets

from utils.exceptions import AlreadyExistsException


async def signup_usecase(
    db_session: Session, user_data: UserSignUp
) -> Dict[str, str]:
    repo = UserRepository(db_session)
    user_hashed = User(**user_data.model_dump(exclude_unset=True), role=UserRoleEnum.client)
    hashed_pwd = await AuthenticationEngine.get_password_hash(user_data.password)
    user_hashed.hashed_password = hashed_pwd
    user = await repo.create_user(user_hashed)
    activity_stats_schema = UserActivityStatsSchema(
        user_id=user.id,
        activity_type=UserActivityTypeEnum.signup,
        action_date=user.created_at
    )
    stats_repository = UserActivityStatsRepository(db_session)
    await stats_repository.create(activity_stats_schema)
    return {
        "access_token": create_access_token(user_id=user.id),
        "refresh_token": create_refresh_token(user_id=user.id),
        "token_type": "bearer",
    }


async def signin_usecase(
    db_session: Session, email: str, password: str, device_id: str
) -> Dict[str, str]:
    repo = UserRepository(db_session)
    user = await repo.get_user_by_email(email)
    await AuthenticationEngine.check_password(user, password)
    activity_stats_schema = UserActivityStatsSchema(
        user_id=user.id,
        activity_type=UserActivityTypeEnum.signin,
        action_date=user.created_at
    )
    stats_repository = UserActivityStatsRepository(db_session)
    await stats_repository.create(activity_stats_schema)
    device_repo = UserDeviceRepository(db_session)
    device_schema = UserDevice(user_id=user.id, device_id=device_id)
    if not await device_repo.does_user_device_exist(user.id, device_id):
        print('\n\n\n HERE \n\n\n')
        await device_repo.create_user_device(device_schema)
        await EmailEngine.send_new_device_email(email='saadatssu@gmail.com', device_id=device_id)
    return {
        "access_token": create_access_token(user_id=user.id),
        "refresh_token": create_refresh_token(user_id=user.id),
        "token_type": "bearer",
    }


async def refresh_tokens_usecase(session: Session, refresh_token: str) -> Dict[str, str]:
    user_repo = UserRepository(session)
    payload = jwt.decode(
        refresh_token,
        settings.refresh_token_secret_key,
        algorithms=[jwt_tokens.ALGORITHM],
    )
    user_id = payload.get("sub")
    await user_repo.get_user_by_id(user_id)
    return {
        'access_token': create_access_token(user_id),
        'refresh_token': create_refresh_token(user_id),
        'token_type': 'bearer',
    }


async def request_password_reset_usecase(db_session: Session, user_email: str):
    repository = UserRepository(db_session)
    user = await repository.get_user_by_email(user_email)
    token = secrets.token_urlsafe(16)
    expires_at = datetime.now(UTC) + timedelta(hours=1)
    token = UserPasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    await repository.create_password_reset_token(token)
    await EmailEngine.send_reset_password_email(user_email, token.token)


async def reset_password_usecase(db_session: Session, token: str, new_password: str) -> None:
    repository = UserRepository(db_session)
    token_from_db = await repository.get_reset_password_token(token)
    new_hashed_password = await AuthenticationEngine.get_password_hash(new_password)
    await repository.update_user_password(token_from_db.user_id,  token_from_db.token, new_hashed_password)
    activity_stats_schema = UserActivityStatsSchema(
        user_id=token_from_db.user_id,
        activity_type=UserActivityTypeEnum.password_reset,
        action_date=datetime.now(UTC)
    )
    stats_repository = UserActivityStatsRepository(db_session)
    await stats_repository.create(activity_stats_schema)


async def update_user_usecase(
    db_session: Session, user_data: User, user_id: int
) -> User:
    repo = UserRepository(db_session)
    await repo.update_user(user_data, user_id)
    activity_stats_schema = UserActivityStatsSchema(
        user_id=user_id,
        activity_type=UserActivityTypeEnum.profile_update,
        action_date=datetime.now(UTC)
    )
    stats_repository = UserActivityStatsRepository(db_session)
    await stats_repository.create(activity_stats_schema)
    return await repo.get_user_by_id(user_id)


async def get_user_activity_logs_usecase(
    db_session: Session, user_email: str = None
) -> List[UserActivityStatsSchema]:
    repo = UserActivityStatsRepository(db_session)
    return await repo.get()
