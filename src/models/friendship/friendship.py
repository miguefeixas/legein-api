from sqlalchemy import Table, Column, ForeignKey

from db import BaseSQL

friendship = Table(
    'friendship',
    BaseSQL.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('friend_id', ForeignKey('user.id'), primary_key=True),
)