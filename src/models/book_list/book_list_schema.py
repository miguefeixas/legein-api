from typing import Optional

from pydantic import BaseModel

from src.models.book import BookBaseSchema


class BookListBaseSchema(BaseModel):
    """Book list base schema."""

    id: int
    name: str


class BookListSchema(BookListBaseSchema):
    """Book list schema."""

    user_id: int
    books: Optional[list[BookBaseSchema]]


class CreateBookListSchema(BaseModel):
    """Create book list schema."""

    name: str
