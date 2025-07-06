from enum import Enum


class UserRoleEnum(str, Enum):
    admin = "admin"
    client = "client"


class UserActivityTypeEnum(str, Enum):
    signin = "signin"
    signup = "signup"
    password_reset = "password_reset"
    profile_update = "profile_update"
