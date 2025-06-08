from datetime import datetime

from sqlalchemy import update
from sqlalchemy.orm import Mapped, mapped_column

from db import BaseSQL


class AccessToken(BaseSQL):
    """
    Access token model
    """

    __tablename__ = 'access_token'

    access_token: Mapped[str] = mapped_column(primary_key=True)
    valid: Mapped[bool]
    expiration: Mapped[datetime]

    @classmethod
    def insert(cls, access_token: str, valid: bool, expiration: datetime) -> None:
        """
        Insert a new access token
        :param access_token:
        :param valid:
        :param expiration:
        """
        new_access_token = cls(access_token=access_token, valid=valid, expiration=expiration)
        cls.session.add(new_access_token)
        cls.session.commit()

    @classmethod
    def find(cls, access_token: str) -> 'AccessToken':
        """
        Find an access token
        :param access_token:
        :return:
        """
        return cls.query.get(access_token)

    @classmethod
    def invalid(cls, token: str) -> None:
        """
        Invalidate an access token
        :param token:
        """
        stmt = update(cls).where(cls.access_token == token).values(valid=False)
        cls.session.execute(stmt)
        cls.session.commit()
