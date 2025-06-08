from datetime import datetime
from typing import Optional, TYPE_CHECKING, Type, List

from sqlalchemy import func, false, select, ForeignKey, column
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Mapped, mapped_column
from db import BaseSQL, SessionLocal, RosettaBaseSubClass


if TYPE_CHECKING:
    from sqlalchemy.orm import Query


class RosettaBase:
    """
    Base class with CRUDL methods

    Every (or almost every) model in the project should inherit from this class
    since it makes it easier to interact with the database.
    """

    query: 'Query'
    session = SessionLocal

    @classmethod
    def find(cls: Type[RosettaBaseSubClass], item_id: any) -> RosettaBaseSubClass | None:
        """
        Find an item by its primary key
        :param item_id:
        :return: an instance of the model or None
        """
        return cls.session.get(cls, item_id)

    @classmethod
    def find_by(cls: Type[RosettaBaseSubClass], filters: List = None) -> RosettaBaseSubClass | None:
        """
        Find an item by its attributes
        :param filters:
        :return: an instance of the model or None
        """
        return cls.session.scalars(select(cls).where(*filters)).first()

    @classmethod
    def list(
        cls: Type[RosettaBaseSubClass], filters: List = None, order_by: (str, bool) = None, limit: int = None
    ) -> list[RosettaBaseSubClass]:
        """
        List all items in the model
        :return: a list of instances of the model
        """
        qry = select(cls)

        if filters:
            qry = qry.where(*filters)

        if order_by:
            order = column(order_by[0])
            qry = qry.order_by(order.asc()) if order_by[1] else qry.order_by(order.desc())

        if limit:
            qry = qry.limit(limit)

        return cls.session.scalars(qry).unique().all()

    def update(self: RosettaBaseSubClass, data: dict[str, any] = None) -> None:
        """
        Update the item in the database.
        """
        if data:
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        self.commit()

    def insert(self: RosettaBaseSubClass) -> RosettaBaseSubClass:
        """
        Insert the item in the database.
        """
        self.session.add(self)
        self.commit()

        return self

    def delete(self: RosettaBaseSubClass) -> None:
        """
        Delete the item from the database.
        """
        self.session.delete(self)
        self.commit()

    def commit(self: RosettaBaseSubClass) -> None:
        """
        Commit the changes to the database.
        """
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise e
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def to_dict(self: RosettaBaseSubClass) -> dict[str, any]:
        """
        Convert the item to a dictionary.
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class RosettaItem(BaseSQL, RosettaBase):
    """
    Base class for every model in the project.
    It contains some common columns that every model should have
    for auditing purposes.
    """

    __abstract__ = True

    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    disabled: Mapped[Optional[bool]] = mapped_column(server_default=false())
    disabled_at: Mapped[Optional[datetime]]
    modified_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now(), onupdate=func.now())

    disabled_by: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id', name='fk_disabled_by'))
    modified_by: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id', name='fk_modified_by'))
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id', name='fk_created_by'))

    def update(self, data: dict[str, any] = None, *args) -> None:
        """
        Update the item in the database.
        """
        self.modified_by = args[0]

        super().update(data)

    def insert(self, *args) -> RosettaBaseSubClass:
        """
        Insert the item in the database.
        """
        self.created_by = args[0]

        return super().insert()

    def enable(self) -> None:
        """
        Enable the item in the database.
        """
        self.disabled = False
        self.disabled_by = None
        self.disabled_at = None
        self.commit()

    def disable(self, *args) -> None:
        """
        Disable the item in the database.
        :param args:
        :return:
        """
        self.disabled = True
        self.disabled_by = args[0]
        self.disabled_at = datetime.now()
        self.commit()

    def add_from_dict(self: RosettaBaseSubClass, data: dict[str, any]) -> None:
        """
        Add the data from a dictionary to the instance.
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
