from typing import Optional

from pydantic import BaseModel

from src.models.book import BookBaseSchema, BookSchema


class BookListBaseSchema(BaseModel):
    """Book list base schema."""

    id: int
    name: str


class BookListSchema(BookListBaseSchema):
    """Book list schema."""

    user_id: int
    books: Optional[list[BookSchema]]


class CreateBookListSchema(BaseModel):
    """Create book list schema."""

    name: str
