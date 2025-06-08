from typing import TYPE_CHECKING, List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.rosetta_item import RosettaItem
from src.models.book_list_book import book_list_book

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.book import Book


class BookList(RosettaItem):
    """Book list model."""

    __tablename__ = 'book_list'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(140))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', name='fk_book_list_user_id', ondelete='CASCADE'))

    user: Mapped['User'] = relationship('User', back_populates='book_lists', foreign_keys=user_id)
    books: Mapped[List['Book']] = relationship(secondary=book_list_book, back_populates='book_lists', cascade='all')
