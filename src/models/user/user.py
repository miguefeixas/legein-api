from datetime import datetime
from typing import Optional, TYPE_CHECKING, List

from sqlalchemy import String, func, ForeignKey, select, case, true
from sqlalchemy.ext.hybrid import hybrid_property

from src.models.base_user import BaseUser

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.friendship import friendship
from src.models.user.user_schema import UserRole
from src.models.author import Author


if TYPE_CHECKING:
    from src.models.notification import Notification
    from src.models.review import Review
    from src.models.book_list import BookList


class User(BaseUser):
    """
    User model
    """

    __tablename__ = 'user'

    name: Mapped[str] = mapped_column(String(60))
    first_last_name: Mapped[str] = mapped_column(String(60))
    second_last_name: Mapped[Optional[str]] = mapped_column(String(60))
    date_of_birth: Mapped[Optional[datetime]]
    user_role: Mapped[UserRole]
    phone_number: Mapped[Optional[str]] = mapped_column(String(12))
    phone_country_code: Mapped[Optional[str]] = mapped_column(String(4))
    username: Mapped[Optional[str]] = mapped_column(String(15))
    profile_picture: Mapped[Optional[str]] = mapped_column(String(1000))

    author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('author.id', name='fk_user_author_id', ondelete='CASCADE')
    )

    reviews: Mapped[list['Review']] = relationship(
        back_populates='user', foreign_keys='Review.user_id', cascade='all, delete'
    )
    author: Mapped['Author'] = relationship('Author', back_populates='user', foreign_keys=author_id)
    notifications: Mapped[List['Notification']] = relationship(
        back_populates='user', foreign_keys='Notification.user_id', cascade='all, delete'
    )
    book_lists: Mapped[List['BookList']] = relationship(
        'BookList', back_populates='user', foreign_keys='BookList.user_id', cascade='all, delete-orphan'
    )

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

    @classmethod
    def list_first_pending(cls) -> list['User']:
        """
        Get all the users but first the pending ones
        :return: All the users but first the pending ones
        """
        qry = select(cls).order_by(case({cls.disabled == true() and cls.created_at == cls.modified_at: 0}, else_=1))

        return cls.session.scalars(qry).all()

    @classmethod
    def get_friends(cls, user_id: int) -> list['User']:
        """
        Get all friends of a user
        :param user_id: The id of the user
        :return: A list of all friends of the user
        """
        stmt = select(User).join(friendship, User.id == friendship.c.friend_id).where(friendship.c.user_id == user_id)
        return cls.session.execute(stmt).scalars().all()
