from typing import Any, List

from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    count: int
    items: List[Any] = []
