from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, UploadFile, File
from google.cloud import storage
from sqlalchemy import false

from src.models.author import AuthorBaseSchema, Author
from src.models.book import Book
from src.models.book.book_schema import BookBaseSchema, BookStatus, BookSchema, CreateBookSchema, UpdateBookSchema
from src.models.genre import Genre
from src.models.publisher import Publisher
from src.models.user import UserSchema, UserRole
from src.routers.auth.auth import get_current_active_user
from src.routers.rosetta_router import create_router
from src.utils.schemas.kpi_schema import create_kpi_schema

api_name = 'book'

router = create_router(api_name)


@router.get('/', response_model=list[BookSchema])
async def get_all_books(current_user: Annotated[UserSchema, Depends(get_current_active_user)]) -> list[Book]:
    """
    Get all books
    :param current_user: The user making the request
    :return: A list of all books
    """
    if current_user.user_role != UserRole.ADMIN and current_user.user_role != UserRole.USER:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    return Book.list_first_pending()


@router.get('/{book_id}/authors', response_model=list[AuthorBaseSchema])
async def get_authors_of_book(
    book_id: str, current_user: Annotated[UserSchema, Depends(get_current_active_user)]
) -> list[Author]:
    """
    Get all authors of a book
    :param book_id: The id of the book
    :param current_user: The user making the request
    :return: A list of all the authors of the book
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    book = Book.find(book_id)

    return book.authors


@router.get('/books-last-seven-days/', response_model=create_kpi_schema(BookBaseSchema))
async def get_last_seven_days_books(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)]
) -> dict[str, int | list[Book]]:
    """
    Get the list of the books created in the last seven days
    :param current_user: The user making the request
    :return: The list of books created in the last seven days
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    fourteen_days_ago = today - timedelta(days=14)

    books_this_week = Book.list([Book.created_at <= today, Book.created_at >= seven_days_ago, Book.disabled == false()])
    total_past_week = Book.list(
        [Book.created_at <= seven_days_ago, Book.created_at >= fourteen_days_ago, Book.disabled == false()]
    )

    return {'total_past_week': len(total_past_week), 'this_week': books_this_week}


@router.get('/pending-books/', response_model=list[BookSchema])
async def get_pending_books(current_user: Annotated[UserSchema, Depends(get_current_active_user)]) -> list[Book]:
    """
    Get all pending books
    :param current_user: The user making the request
    :return: A list of all pending books
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    return Book.list([Book.status == BookStatus.PENDING])


@router.post('/', response_model=BookSchema)
async def create_book(
    book: CreateBookSchema, current_user: Annotated[UserSchema, Depends(get_current_active_user)]
) -> Book:
    """
    Create a new book
    :param book: The book to create
    :param current_user: The user making the request
    :return: The created book
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    new_book = Book()
    new_book.add_from_dict(book.dict())

    for author_id in book.author_ids:
        author = Author.find(author_id)
        new_book.authors.append(author)

    main_genre = Genre.find(book.main_genre_id)
    new_book.genres.append(main_genre)

    if book.secondary_genre_id:
        secondary_genre = Genre.find(book.secondary_genre_id)
        new_book.genres.append(secondary_genre)

    Book.insert(new_book, current_user.id)

    return new_book


@router.patch('/upload-image/{book_id}')
async def upload_image(
    book_id: str,
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
    file: UploadFile = File(...),  # noqa: B008
) -> None:
    """
    Upload an image for a book
    :param book_id: The id of the book
    :param current_user: The user making the request
    :param file: The image file to upload
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    storage_client = storage.Client(project='legein-gcp')
    bucket = storage_client.get_bucket('legein-dev')

    blob_name = f'cover_images/{book_id}'

    try:
        # Check if the directory exists
        blobs = storage_client.list_blobs('legein-dev', prefix=blob_name)
        for blob in blobs:
            blob.reload()
            generation_match_precondition = blob.generation

            blob.delete(if_generation_match=generation_match_precondition)

        blob_name = f'cover_images/{book_id}/{file.filename}'
        new_blob = bucket.blob(blob_name)

        new_blob.upload_from_file(file.file, content_type=file.content_type)
        new_blob.make_public()

        file_url = new_blob.public_url

        book = Book.find(book_id)
        book.cover = file_url
        Book.update(book, None, current_user.id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'An error occurred while uploading the image: {str(e)}') from None


@router.get('/{book_id}', response_model=BookSchema)
async def get_book(book_id: str, current_user: Annotated[UserSchema, Depends(get_current_active_user)]) -> Book:
    """
    Get a book by its id
    :param book_id: The id of the book
    :param current_user: The user making the request
    :return: The book
    """
    if current_user.user_role != UserRole.ADMIN and current_user.user_role != UserRole.USER:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    return Book.find(book_id)


@router.put('/{book_id}', response_model=BookSchema)
async def update_book(
    book_id: str, book: UpdateBookSchema, current_user: Annotated[UserSchema, Depends(get_current_active_user)]
) -> Book:
    """
    Update a book
    :param book_id: The id of the book
    :param book: The updated book
    :param current_user: The user making the request
    :return: The updated book
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    # Update the book itself
    book_to_update = Book.find(book_id)
    updated_book = book.dict()

    # Update the authors
    authors = []
    for author_id in book.author_ids:
        author = Author.find(author_id)
        authors.append(author)
    updated_book['authors'] = authors

    # Update the genres
    genres = []
    main_genre = Genre.find(book.main_genre_id)
    genres.append(main_genre)
    if book.secondary_genre_id:
        secondary_genre = Genre.find(book.secondary_genre_id)
        genres.append(secondary_genre)

    updated_book['genres'] = genres

    # Update the publisher
    if book.publisher_id:
        publisher = Publisher.find(book.publisher_id)
        updated_book['publisher'] = publisher

    Book.update(book_to_update, updated_book, current_user.id)

    return book_to_update


@router.get('/random/', response_model=BookSchema)
async def get_random_book() -> Book:
    """
    Get a random book
    :return: A random book
    """
    return Book.get_random_book()
