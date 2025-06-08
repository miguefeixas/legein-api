from typing import Annotated

from fastapi import Depends, HTTPException

from src.models.book_list import BookList, BookListSchema, BookListBaseSchema, CreateBookListSchema
from src.models.book import Book
from src.models.user import UserSchema
from src.routers.auth.auth import get_current_active_user
from src.routers.rosetta_router import create_router

api_name = 'book-list'

router = create_router(api_name)


@router.post('/', response_model=BookListSchema)
async def create_book_list(
    book_list: CreateBookListSchema,
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
) -> BookList:
    """Create a new book list for the current user."""
    new_list = BookList(name=book_list.name, user_id=current_user.id)
    BookList.insert(new_list, current_user.id)
    return new_list


@router.get('/user', response_model=list[BookListSchema])
async def get_user_book_lists(current_user: Annotated[UserSchema, Depends(get_current_active_user)]) -> list[BookList]:
    """Return all book lists of a user."""

    return BookList.list([BookList.user_id == current_user.id])


@router.get('/{list_id}', response_model=BookListSchema)
async def get_book_list(list_id: int) -> BookList:
    """Get a book list by id."""
    book_list = BookList.find(list_id)
    if not book_list:
        raise HTTPException(status_code=404, detail='Book list not found')
    return book_list


@router.post('/{list_id}/books/{book_id}', response_model=BookListSchema)
async def add_book_to_list(
    list_id: int,
    book_id: int,
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
) -> BookList:
    """Add a book to a list."""
    book_list = BookList.find(list_id)
    if not book_list or book_list.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Not enough permissions')
    book = Book.find(book_id)
    book_list.books.append(book)
    BookList.update(book_list, None, current_user.id)
    return book_list


@router.delete('/{list_id}/books/{book_id}', response_model=BookListSchema)
async def remove_book_from_list(
    list_id: int,
    book_id: int,
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
) -> BookList:
    """Remove a book from a list."""
    book_list = BookList.find(list_id)
    if not book_list or book_list.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Not enough permissions')
    book = Book.find(book_id)
    if book in book_list.books:
        book_list.books.remove(book)
        BookList.update(book_list, None, current_user.id)
    return book_list
