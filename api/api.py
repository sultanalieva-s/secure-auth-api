from fastapi import APIRouter
from api import template_endpoints as example_router
from api import users_endpoints as user_router
router = APIRouter()


router.include_router(
    user_router.router,
    prefix='/users',
    tags=["Users"],
)