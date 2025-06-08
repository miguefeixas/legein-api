from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import false

from src.models.author import AuthorBaseSchema, Author
from src.models.book import Book
from src.models.book.book_schema import BookBaseSchema
from src.models.user import UserRole
from src.models.user import UserSchema
from src.routers.auth.auth import get_current_active_user
from src.routers.rosetta_router import create_router


api_name = 'author'

router = create_router(api_name)


@router.get('/', response_model=list[AuthorBaseSchema])
async def get_all_authors(current_user: Annotated[UserSchema, Depends(get_current_active_user)]) -> list[Author]:
    """
    Get all authors
    :param current_user: The user making the request
    :return: A list of all authors
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    return Author.list([Author.disabled == false()], ('name', True))


@router.get('/{author_id}/books', response_model=list[BookBaseSchema])
async def get_books_of_author(
    author_id: str, current_user: Annotated[UserSchema, Depends(get_current_active_user)]
) -> list[Book]:
    """
    Get all books of an author
    :param author_id: The id of the author
    :param current_user: The user making the request
    :return: A list of books that the author has written
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    author = Author.find(author_id)

    return author.books
