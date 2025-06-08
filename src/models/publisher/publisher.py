from typing import TYPE_CHECKING, List

from sqlalchemy import String

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.rosetta_item import RosettaItem

if TYPE_CHECKING:
    from src.models.book import Book


class Publisher(RosettaItem):
    """
    Publisher model
    """

    __tablename__ = 'publisher'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(140))

    books: Mapped[List['Book']] = relationship(
        'Book', back_populates='publisher', foreign_keys='Book.publisher_id', cascade='all, delete-orphan'
    )
