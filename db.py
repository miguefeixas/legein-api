from typing import TypeVar, TYPE_CHECKING

import toml

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, scoped_session

if TYPE_CHECKING:
    from src.models.rosetta_item import RosettaItem, RosettaBase

with open('./configs/.secrets.local.toml', 'r') as f:
    config = toml.load(f)

SQLALCHEMY_DATABASE_URL = config['database']['DB_URL']

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


class BaseSQL(DeclarativeBase):
    """
    Base class for SQL models
    """

    query = SessionLocal.query_property()
    session = SessionLocal


RosettaBaseSubClass = TypeVar('RosettaBaseSubClass', bound='RosettaBase')
RosettaItemSubClass = TypeVar('RosettaItemSubClass', bound='RosettaItem')
