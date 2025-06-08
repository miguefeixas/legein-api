from enum import Enum
from typing import Optional

from pydantic import BaseModel

from src.models.author.author_schema import AuthorBaseSchema
from src.models.genre import GenreBaseSchema
from src.models.publisher import PublisherBaseSchema


class BookStatus(Enum):
    ACTIVE = 'ACTIVE'
    PENDING = 'PENDING'
    REJECTED = 'REJECTED'
    DELETED = 'DELETED'


class BookBaseSchema(BaseModel):
    """
    Book base schema
    """

    id: int
    title: str
    overview: str


class UpdateBookSchema(BookBaseSchema):
    """
    Update book schema
    """

    isbn: str
    status: BookStatus
    overview: str
    publication_year: int
    pages: int
    publisher_id: Optional[int]
    language: Optional[str]
    author_ids: list[int]
    main_genre_id: int
    secondary_genre_id: Optional[int]


class BookSchema(BookBaseSchema):
    """
    Book schema
    """

    isbn: str
    status: BookStatus
    overview: str
    publication_year: int
    pages: int
    publisher_id: Optional[int]
    cover: Optional[str]
    publisher: Optional[PublisherBaseSchema]
    authors: Optional[list[AuthorBaseSchema]]
    genres: Optional[list[GenreBaseSchema]]
    language: Optional[str]


class CreateBookSchema(BaseModel):
    """
    Create book schema
    """

    title: str
    isbn: str
    author_ids: list[int]
    publisher_id: Optional[int]
    main_genre_id: int
    secondary_genre_id: int
    pages: int
    language: str
    overview: str
    publication_year: int
