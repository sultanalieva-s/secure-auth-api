from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.mysql import TIMESTAMP, ENUM
from resource_access.db_models.base_model import Base
from schemas.enums.user_enums import UserRoleEnum, UserActivityTypeEnum


class UserDB(Base):
    __tablename__ = "users"

    first_name = Column(String(150))
    last_name = Column(String(150))
    email = Column(String(100), unique=True)
    phone = Column(String(100), unique=True)
    hashed_password = Column(String(300))
    role = Column(ENUM(UserRoleEnum, name="user_role_enum"))
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UserActivityStats(Base):
    __tablename__ = "user_activity_stats"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    activity_type = Column(
        ENUM(UserActivityTypeEnum, name="user_activity_type_enum"),
    )
    action_date = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
