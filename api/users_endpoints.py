from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from api.depends import get_session
from core import jwt_tokens
from core.config import settings
from schemas.user_schemas import UserSignUp, TokenSchema, UserSignIn, TokenPayload, RefreshTokenRequest, \
    PasswordResetRequestSchema, PasswordResetSchema
from usecases.user_usecases import signup_usecase, signin_usecase, refresh_tokens_usecase, \
    request_password_reset_usecase, reset_password_usecase
from utils.exceptions import NotFoundException, AuthenticationError, AlreadyExistsException
from jose import jwt, JWTError

router = APIRouter()


@router.post(
    '/signup/',
    status_code=status.HTTP_200_OK,
    description='User Registration',
    response_model=TokenSchema,
)
async def user_signup(
    user_data: UserSignUp,
    db_session: Session = Depends(get_session),
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
):
    try:
        await reset_password_usecase(db_session, data.token, data.new_password)
        return {"message": "Password reset successful"}
    except NotFoundException as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": e.message, "error_code": e.error_code},
        )
