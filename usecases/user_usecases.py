from datetime import datetime, UTC, timedelta
from typing import Dict

from sqlalchemy.orm import Session

from core import jwt_tokens
from core.config import settings
from core.jwt_tokens import create_access_token, create_refresh_token
from engines.auth_engine import AuthenticationEngine
from engines.email_engine import EmailEngine
from resource_access import db_session
from resource_access.repositories.user_repos import UserRepository
from schemas.enums.user_enums import UserRoleEnum
from schemas.user_schemas import UserSignUp, User, UserUpdate, TokenPayload, UserPasswordResetToken
from jose import jwt
import secrets


async def signup_usecase(
    db_session: Session, user_data: UserSignUp
) -> Dict[str, str]:
    repo = UserRepository(db_session)
    user_hashed = User(**user_data.model_dump(exclude_unset=True), role=UserRoleEnum.client)
    hashed_pwd = await AuthenticationEngine.get_password_hash(user_data.password)
    user_hashed.hashed_password = hashed_pwd
    user = await repo.create_user(user_hashed)
    return {
        "access_token": create_access_token(user_id=user.id),
        "refresh_token": create_refresh_token(user_id=user.id),
        "token_type": "bearer",
    }


async def signin_usecase(
    db_session: Session, email: str, password: str
) -> Dict[str, str]:
    repo = UserRepository(db_session)
    user = await repo.get_user_by_email(email)
    await AuthenticationEngine.check_password(user, password)
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


async def user_update_usecase(
    db_session: Session, user_data: UserUpdate
) -> Dict[str, str]:
    repo = UserRepository(db_session)
    return repo.update_user(user_data)

