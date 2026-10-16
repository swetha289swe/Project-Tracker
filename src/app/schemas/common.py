

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

class Pagination(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int