from sqlalchemy import Table, Column, ForeignKey

from db import BaseSQL

book_genre = Table(
    'book_genre',
    BaseSQL.metadata,
    Column('book_id', ForeignKey('book.id'), primary_key=True),
    Column('genre_id', ForeignKey('genre.id'), primary_key=True),
)
