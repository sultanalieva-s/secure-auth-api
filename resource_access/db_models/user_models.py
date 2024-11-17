from datetime import datetime, UTC

from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    func,
    DateTime,
)
from sqlalchemy.dialects.mysql import TIMESTAMP, ENUM
from sqlalchemy.orm import relationship

from resource_access.db_models.base_model import Base
from schemas.enums.user_enums import UserRoleEnum, UserActivityTypeEnum
import pytz


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
    login_otp = Column(String(100), nullable=True)
    login_otp_created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    password_reset_tokens = relationship(
        'UserPasswordResetTokenDB',
        back_populates='user',
        lazy='selectin',
        uselist=True,
    )


class UserActivityStats(Base):
    __tablename__ = "user_activity_stats"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    activity_type = Column(
        ENUM(UserActivityTypeEnum, name="user_activity_type_enum"),
    )
    action_date = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class UserPasswordResetTokenDB(Base):
    __tablename__ = "user_password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(100), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    user = relationship("UserDB", back_populates="password_reset_tokens")

    def is_valid(self):
        return datetime.now(UTC) < self.expires_at.replace(tzinfo=pytz.UTC)


class UserDeviceDB(Base):
    __tablename__ = "user_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(String(200), unique=True, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

