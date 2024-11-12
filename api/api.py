from fastapi import APIRouter
from api import template_endpoints as example_router
router = APIRouter()


router.include_router(
    example_router.router,
    prefix="/example",
    tags=["Example"],
)
