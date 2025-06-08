from datetime import datetime

from pydantic import BaseModel

from src.models.book import BookSchema
from src.models.user import UserSchema


class ReviewBaseSchema(BaseModel):
    """
    Review base schema
    """

    id: int
    title: str
    content: str


class ReviewSchema(ReviewBaseSchema):
    """
    Review schema
    """

    rating: int
    book_id: int
    user_id: int
    disabled: bool
    book: BookSchema
    user: UserSchema
    created_at: datetime


class UpdateReviewSchema(ReviewBaseSchema):
    """
    Update review schema
    """

    rating: int
    book_id: int
    user_id: int
    disabled: bool


class CreateReviewSchema(BaseModel):
    """Create review schema."""

    title: str
    content: str
    rating: int
    book_id: int
