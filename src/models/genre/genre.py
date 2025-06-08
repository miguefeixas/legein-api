from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String


from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.book_genre import book_genre
from src.models.rosetta_item import RosettaItem

if TYPE_CHECKING:
    from src.models.book import Book


class Genre(RosettaItem):
    """
    Genre model
    """

    __tablename__ = 'genre'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(60))
    description: Mapped[Optional[str]] = mapped_column(String(500))

    books: Mapped[List['Book']] = relationship(secondary=book_genre, back_populates='genres')
