from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.rosetta_item import RosettaItem

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.book import Book

class NotificationType(Enum):
    FRIENDSHIP = 'FRIENDSHIP'
    REVIEW = 'REVIEW'


class Notification(RosettaItem):
    """
    Notification model
    """

    __tablename__ = 'notification'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    notification_type: Mapped[NotificationType]

    friend_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('user.id', name='fk_notification_friend_id', ondelete='CASCADE')
    )
    book_id: Mapped[Optional[int]] = mapped_column(ForeignKey('book.id', name='fk_notification_book_id', ondelete='CASCADE'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', name='fk_notification_user_id', ondelete='CASCADE'))

    friend: Mapped['User'] = relationship('User', foreign_keys='Notification.friend_id')
    book: Mapped['Book'] = relationship('Book', foreign_keys='Notification.book_id')
    user: Mapped['User'] = relationship('User', back_populates='notifications', foreign_keys='Notification.user_id')

