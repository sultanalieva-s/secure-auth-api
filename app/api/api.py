from fastapi import APIRouter
from app.api import template_endpoints as example_router
from app.api import users_endpoints as user_router

router = APIRouter()


router.include_router(
    user_router.router,
    prefix="/users",
    tags=["Users"],
)
