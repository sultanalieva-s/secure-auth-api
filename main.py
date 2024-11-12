from fastapi import FastAPI

from dotenv import dotenv_values
from api.api import router
config = dotenv_values(".env")


app = FastAPI(title="authentication api")


def ignore_handler(payload, **kw):  # kw is currently unused
    try:
        exception = payload["data"]["body"]["trace"]["exception"]["class"]
        if exception in ["RequestValidationError", "HTTPException"]:
            return False
    except KeyError:
        return payload
    return payload


app.include_router(router)
