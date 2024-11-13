from typing import Union

from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy.orm import Session

from api.depends import get_session

app = FastAPI()

router = APIRouter()


@router.get("/")
async def read_root(
        session: Session = Depends(get_session),
):
    return {"Hello": "World"}


@router.get("/items/{item_id}")
async def read_item(
        item_id: int,
        session: Session = Depends(get_session),
        q: Union[str, None] = None
):
    return {"item_id": item_id, "q": q}
