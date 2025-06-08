from sqlalchemy import Table, Column, ForeignKey

from db import BaseSQL

author_book = Table(
    'author_book',
    BaseSQL.metadata,
    Column('author_id', ForeignKey('author.id'), primary_key=True),
    Column('book_id', ForeignKey('book.id'), primary_key=True),
)
