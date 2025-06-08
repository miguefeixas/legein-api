from sqlalchemy import Table, Column, ForeignKey

from db import BaseSQL

book_list_book = Table(
    'book_list_book',
    BaseSQL.metadata,
    Column('book_list_id', ForeignKey('book_list.id', ondelete='CASCADE'), primary_key=True),
    Column('book_id', ForeignKey('book.id', ondelete='CASCADE'), primary_key=True),
)
