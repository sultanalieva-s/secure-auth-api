from math import ceil
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, Request, Response, status, HTTPException

from dotenv import dotenv_values
from fastapi_limiter import FastAPILimiter
from prometheus_fastapi_instrumentator import Instrumentator

from api.api import router
config = dotenv_values(".env")

REDIS_URL = "redis://redis-secure-auth:6379"


async def service_name_identifier(request: Request):
    service = request.headers.get("Service-Name")
    return service


async def custom_callback(request: Request, response: Response, pexpire: int):
    """
    default callback when too many requests
    :param request:
    :param pexpire: The remaining milliseconds
    :param response:
    :return:
    """
    expire = ceil(pexpire / 1000)

    raise HTTPException(
        status.HTTP_429_TOO_MANY_REQUESTS,
        f"Too Many Requests. Retry after {expire} seconds.",
        headers={"Retry-After": str(expire)},
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_connection = redis.from_url(REDIS_URL, encoding="utf8")
    await FastAPILimiter.init(
        redis=redis_connection,
        identifier=service_name_identifier,
        http_callback=custom_callback,
    )
    yield
    await FastAPILimiter.close()


app = FastAPI(title="Secure Authentication Api", lifespan=lifespan)

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)


def ignore_handler(payload, **kw):  # kw is currently unused
    try:
        exception = payload["data"]["body"]["trace"]["exception"]["class"]
        if exception in ["RequestValidationError", "HTTPException"]:
            return False
    except KeyError:
        return payload
    return payload


app.include_router(router)
