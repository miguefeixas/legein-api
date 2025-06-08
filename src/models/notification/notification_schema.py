
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel

from src.models.notification import NotificationType
from src.models.user import UserSchema
from src.models.book import BookSchema


class NotificationSchema(BaseModel):
    """
    Notification schema
    """

    id: int
    notification_type: NotificationType
    user_id: int
    friend_id: Optional[int] = None
    book_id: Optional[int] = None
    user: UserSchema
    friend: Optional[UserSchema] = None
    book: Optional[BookSchema] = None
