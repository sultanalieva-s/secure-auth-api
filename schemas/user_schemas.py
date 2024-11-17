from datetime import datetime

from pydantic import BaseModel, EmailStr
from typing import Optional, List

from schemas.enums.user_enums import UserRoleEnum, UserActivityTypeEnum


class User(BaseModel):
    id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[UserRoleEnum] = None
    hashed_password: Optional[str] = None
    is_deleted: Optional[bool] = None
    login_otp: Optional[str] = None
    login_otp_created_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserSignUp(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]


class TokenSchema(BaseModel):
    access_token: Optional[str]
    refresh_token: Optional[str]
    token_type: Optional[str]


class UserSignIn(BaseModel):
    email: EmailStr
    password: str
    device_id: str


class UserSignInOTP(BaseModel):
    email: EmailStr
    otp: str


class TokenPayload(BaseModel):
    sub: int
    dev: Optional[str]
    hpt: Optional[str]


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class SuccessResponse(BaseModel):
    message: str


class PasswordResetRequestSchema(BaseModel):
    email: EmailStr


class PasswordResetSchema(BaseModel):
    token: str
    new_password: str


class UserPasswordResetToken(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    token: Optional[str] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserActivityStatsSchema(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    activity_type: Optional[UserActivityTypeEnum]
    action_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdateIn(BaseModel):
    first_name: str
    last_name: str
    phone: str


class UserUpdateOut(BaseModel):
    id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


class UserDevice(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    device_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

