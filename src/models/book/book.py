from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, ForeignKey, case, func, false

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .book_schema import BookStatus
from src.models.book_genre import book_genre
from src.models.rosetta_item import RosettaItem
from src.models.author_book import author_book
from src.models.genre import Genre
from src.models.publisher import Publisher

if TYPE_CHECKING:
    from src.models.author import Author
    from src.models.review import Review


class Book(RosettaItem):
    """
    Book model
    """

    __tablename__ = 'book'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(140))
    overview: Mapped[str] = mapped_column(String(1200))
    isbn: Mapped[str] = mapped_column(String(20))
    publication_year: Mapped[Optional[int]]
    pages: Mapped[Optional[int]]
    cover: Mapped[Optional[str]] = mapped_column(String(1000))
    language: Mapped[Optional[str]] = mapped_column(String(20))
    status: Mapped[Optional[BookStatus]] = mapped_column(default=BookStatus.PENDING)

    publisher_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('publisher.id', name='fk_book_publisher_id', ondelete='CASCADE')
    )

    authors: Mapped[List['Author']] = relationship(secondary=author_book, back_populates='books')
    genres: Mapped[List[Genre]] = relationship(secondary=book_genre, back_populates='books')
    reviews: Mapped[List['Review']] = relationship(
        back_populates='book', foreign_keys='Review.book_id', cascade='all, delete'
    )
    publisher: Mapped['Publisher'] = relationship('Publisher', back_populates='books', foreign_keys=publisher_id)

    @classmethod
    def list_first_pending(cls) -> list['Book']:
        """
        Get all the books but first the pending ones
        :return: All the books but first the pending ones
        """
        qry = cls.session.query(cls).order_by(case({cls.status == BookStatus.PENDING: 0}, else_=1))

        return cls.session.scalars(qry).all()

    @classmethod
    def get_random_book(cls):
        """
        Get a random book
        :return: A random book
        """
        # return cls.session.query(cls).where(cls.disabled == false()).order_by(func.random()).first()
        return cls.session.query(cls).where(cls.id == 17).first()
