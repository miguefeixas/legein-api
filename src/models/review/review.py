from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.rosetta_item import RosettaItem

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.book import Book


class Review(RosettaItem):
    """
    Review model
    """

    __tablename__ = 'review'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(140))
    content: Mapped[str] = mapped_column(String(2000))
    rating: Mapped[int]

    book_id: Mapped[int] = mapped_column(ForeignKey('book.id', name='fk_review_book_id', ondelete='CASCADE'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', name='fk_review_user_id', ondelete='CASCADE'))

    book: Mapped['Book'] = relationship('Book', back_populates='reviews', foreign_keys='Review.book_id')
    user: Mapped['User'] = relationship('User', back_populates='reviews', foreign_keys='Review.user_id')
