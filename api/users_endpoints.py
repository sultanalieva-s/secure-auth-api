from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from api.depends import get_session, get_current_user
from core.config import settings
from schemas.user_schemas import UserSignUp, TokenSchema, UserSignIn, RefreshTokenRequest, \
    PasswordResetRequestSchema, PasswordResetSchema, UserUpdateOut, UserUpdateIn, User, UserActivityStatsSchema
from usecases.user_usecases import signup_usecase, signin_usecase, refresh_tokens_usecase, \
    request_password_reset_usecase, reset_password_usecase, update_user_usecase, get_user_activity_logs_usecase
from utils.exceptions import NotFoundException, AuthenticationError, AlreadyExistsException
from jose import JWTError

router = APIRouter()

from fastapi_limiter.depends import RateLimiter

RATE_LIMIT_DEFAULT_REQUESTS = settings.rate_limit_requests
RATE_LIMIT_DEFAULT_SECONDS = settings.rate_limit_seconds


@router.post(
    '/signup/',
    status_code=status.HTTP_200_OK,
    description='User Registration',
    response_model=TokenSchema,
)
async def user_signup(
        user_data: UserSignUp,
        db_session: Session = Depends(get_session),
        _=Depends(RateLimiter(times=RATE_LIMIT_DEFAULT_REQUESTS, seconds=RATE_LIMIT_DEFAULT_SECONDS)),
):
    try:
        return await signup_usecase(
            db_session,
            user_data,
        )
    except AlreadyExistsException as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": e.message, "error_code": e.error_code},
        )


@router.post(
    '/signin/',
    status_code=status.HTTP_200_OK,
    description='User Signin',
    response_model=TokenSchema,
)
async def signin(
        signin_data: UserSignIn,
        db_session: Session = Depends(get_session),
        _=Depends(RateLimiter(times=RATE_LIMIT_DEFAULT_REQUESTS, seconds=RATE_LIMIT_DEFAULT_SECONDS)),
):
    try:
        return await signin_usecase(
            db_session,
            email=signin_data.email,
            password=signin_data.password,
        )
    except NotFoundException as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": e.message, "error_code": e.error_code},
        )
    except AuthenticationError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": e.message, "error_code": e.error_code},
        )


@router.post(
    "/refresh-tokens",
    response_model=TokenSchema
)
async def refresh_tokens(
        request: RefreshTokenRequest,
        db_session: Session = Depends(get_session),
        _=Depends(RateLimiter(times=RATE_LIMIT_DEFAULT_REQUESTS, seconds=RATE_LIMIT_DEFAULT_SECONDS)),
):
    try:
        return await refresh_tokens_usecase(db_session, request.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except NotFoundException as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": e.message, "error_code": e.error_code},
        )


@router.post("/password-reset/request")
async def request_password_reset(
        data: PasswordResetRequestSchema,
        db_session: Session = Depends(get_session),
        _=Depends(RateLimiter(times=RATE_LIMIT_DEFAULT_REQUESTS, seconds=RATE_LIMIT_DEFAULT_SECONDS)),
):
    try:
        await request_password_reset_usecase(db_session, data.email)
        return {"message": "Password reset email sent"}
    except NotFoundException as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": e.message, "error_code": e.error_code},
        )


@router.post("/password-reset/confirm")
async def reset_password(
        data: PasswordResetSchema,
        db_session: Session = Depends(get_session),
        _=Depends(RateLimiter(times=RATE_LIMIT_DEFAULT_REQUESTS, seconds=RATE_LIMIT_DEFAULT_SECONDS)),
):
    try:
        await reset_password_usecase(db_session, data.token, data.new_password)
        return {"message": "Password reset successful"}
    except NotFoundException as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": e.message, "error_code": e.error_code},
        )


@router.put(
    "/",
    description="Update User",
    response_model=UserUpdateOut,
    status_code=status.HTTP_200_OK,
)
async def update_user(
        user_in: UserUpdateIn,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session),
        _=Depends(RateLimiter(times=RATE_LIMIT_DEFAULT_REQUESTS, seconds=RATE_LIMIT_DEFAULT_SECONDS)),
):
    new_user_data = User(**user_in.dict(exclude_unset=True))
    try:
        return await update_user_usecase(session, new_user_data, current_user.user_id)
    except NotFoundException as error:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": error.message,
                "error_code": error.error_code,
            },
        )
    except AlreadyExistsException as error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": error.message,
                "error_code": error.error_code,
            },
        )


@router.get(
    "/user-activity/",
    description="Get User Activity Logs",
    response_model=List[UserActivityStatsSchema],
    status_code=status.HTTP_200_OK,
)
async def get_user_activity(
        session: Session = Depends(get_session),
        _=Depends(RateLimiter(times=RATE_LIMIT_DEFAULT_REQUESTS, seconds=RATE_LIMIT_DEFAULT_SECONDS)),
):
    return await get_user_activity_logs_usecase(session)