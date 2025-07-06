from typing import Any, List

from schemas.pagination_schemas import PaginatedResponse


def paginate(count: int, items: List[Any]):
    return PaginatedResponse(count=count, items=items)
