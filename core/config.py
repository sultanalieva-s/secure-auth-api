import os
from typing import List, Optional, Union

from pydantic import validator
from pydantic_settings import BaseSettings

from core.constants.environment_constants import DEV, PROD, STAGING


class Settings(BaseSettings):
    environment: str = DEV

    @validator("environment")
    def environment_values(cls, v):
        if v is None:
            return None
        if v not in [PROD, STAGING, DEV]:
            raise ValueError(f"Incorrect environment value: {v}")
        return v

    mysql_async_url: str = 'mysql+aiomysql://user:test123@mysql_db:3306/secure_auth_db'
    mysql_url: str = 'mysql+pymysql://user:test123@mysql_db:3306/secure_auth_db'
    SQLALCHEMY_DATABASE_URI: str = mysql_url

    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    media_directory: str = os.path.join(base_dir, "media")
    domain_name: str = "localhost:5000"
    frontend_domain_name: str = "localhost:3000"
    api_v1_path: str = "/api/v1"

    db_async_pool_size: int = 8
    db_async_pool_recycle: int = -1
    db_async_max_overflow: int = 7

    db_sync_pool_size: int = 5
    db_sync_pool_recycle: int = -1
    db_sync_max_overflow: int = 5

    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = (
        60 * 24 * 30
    )  # 60 minutes * 24 hours * 90 days = 30 days
    access_token_secret_key: str = "ssd"
    refresh_token_secret_key: str = "sadd"

    rate_limit_requests: int = 3
    rate_limit_seconds: int = 20

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://local.dockertoolbox.tiangolo.com"]'
    backend_cors_origins: List[str] = ["*"]

    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    project_name: str = "Secure Authentication"
    default_pagination_limit: int = 10


settings = Settings()

logging_conf = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "{name} {levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "console"},
    },
    "loggers": {
        "": {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "handlers": [
                "console",
            ],
            "propagate": True,
        }
    },
}
