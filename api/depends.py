from resource_access.repositories.user_repos import UserRepository
from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import HTTPBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from core.config import settings

from schemas.user_schemas import TokenPayload, User
from resource_access.db_session import AsyncSessionLocal

from core import jwt_tokens
from utils.exceptions import NotFoundException

httpbearer_schema = HTTPBearer()


async def get_session() -> Session:
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_refresh_token_data(
    token: str = Depends(httpbearer_schema),
) -> TokenPayload:
    try:
        print(f'\n\n\n{token}\n\n\n')
        payload = jwt.decode(
            token.credentials,
            settings.refresh_token_secret_key,
            algorithms=[jwt_tokens.ALGORITHM],
        )
        return TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )


async def validate_refresh_token(
    token: TokenPayload = Depends(get_refresh_token_data),
) -> TokenPayload:
    try:
        async with AsyncSessionLocal() as session:
            user_repo = UserRepository(session)
            user = await user_repo.get_user_by_id(token.sub)
        if user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='User is not active'
            )
        return token
    except NotFoundException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Could not validate credentials',
        )


async def get_token_data(token: str = Depends(httpbearer_schema)) -> TokenPayload:
    try:
        payload = jwt.decode(
            token.credentials,
            settings.access_token_secret_key,
            algorithms=[jwt_tokens.ALGORITHM],
        )
        return TokenPayload(**payload)
    except jwt.JWTError as e:
        print(f'\n\n\n{e}\n\n\n')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: TokenPayload = Depends(get_token_data),
    db_session: Session = Depends(get_session),
) -> User:
    try:
        user_repo = UserRepository(db_session)
        user_from_repo = await user_repo.get_user_by_id(token.sub)
        return user_from_repo
    except NotFoundException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
