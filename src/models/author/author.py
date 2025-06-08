from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, func
from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.rosetta_item import RosettaItem
from src.models.author_book import author_book

from src.models.book import Book

if TYPE_CHECKING:
    from src.models.user import User


class Author(RosettaItem):
    """
    Author model
    """

    __tablename__ = 'author'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(60))
    first_last_name: Mapped[str] = mapped_column(String(60))
    second_last_name: Mapped[Optional[str]] = mapped_column(String(60))
    date_of_birth: Mapped[Optional[datetime]]
    country: Mapped[Optional[str]] = mapped_column(String(60))
    city: Mapped[Optional[str]] = mapped_column(String(60))
    biography: Mapped[Optional[str]] = mapped_column(String(1200))
    picture: Mapped[Optional[str]] = mapped_column(String(1000))

    books: Mapped[List[Book]] = relationship(secondary=author_book, back_populates='authors', cascade='all, delete')
    user: Mapped['User'] = relationship('User', back_populates='author', foreign_keys='User.author_id')

    @hybrid_property
    def full_name(self) -> str:
        """
        Get the full name of the user
        :return: The full name of the user
        """
        return f'{self.name} {self.first_last_name} {self.second_last_name or ""}'

    @full_name.expression
    def full_name(cls) -> str:  # noqa: N805
        """
        Get the full name of the user in a query
        :return: The full name of the user
        """
        return func.concat(cls.name, ' ', cls.first_last_name, ' ', func.coalesce(cls.second_last_name, ''))
