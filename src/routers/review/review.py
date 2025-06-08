from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import false
from werkzeug.exceptions import abort

from src.models.review import (
    ReviewSchema,
    Review,
    ReviewBaseSchema,
    UpdateReviewSchema,
    CreateReviewSchema,
)
from src.models.user import UserSchema, UserRole, User
from src.routers.auth.auth import get_current_active_user
from src.routers.rosetta_router import create_router
from src.utils.schemas.kpi_schema import create_kpi_schema

api_name = 'review'

router = create_router(api_name)


@router.get('/{review_id}', response_model=ReviewSchema)
async def get_review_by_id(
    review_id: int, current_user: Annotated[UserSchema, Depends(get_current_active_user)]
) -> Review:
    """
    Get a review by its id
    :param review_id: The id of the review
    :param current_user: The user making the request
    :return: The review with the given id
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    return Review.find(review_id)


@router.get('/reviews-last-seven-days/', response_model=create_kpi_schema(ReviewBaseSchema))
async def get_last_seven_days_reviews(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
) -> dict[str, int | list[Review]]:
    """
    Get the list of the reviews created in the last seven days
    :param current_user: The user making the request
    :return: The list of reviews created in the last seven days
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    fourteen_days_ago = today - timedelta(days=14)

    reviews_this_week = Review.list(
        [Review.created_at <= today, Review.created_at >= seven_days_ago, Review.disabled == false()]
    )
    total_past_week = Review.list(
        [Review.created_at <= seven_days_ago, Review.created_at >= fourteen_days_ago, Review.disabled == false()]
    )

    return {'total_past_week': len(total_past_week), 'this_week': reviews_this_week}


@router.get('/', response_model=list[ReviewSchema])
async def get_all_reviews(current_user: Annotated[UserSchema, Depends(get_current_active_user)]) -> list[Review]:
    """
    Get all reviews
    :param current_user: The user making the request
    :return: A list of all reviews
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    return Review.list()


@router.post('/', response_model=ReviewSchema)
async def create_review(
    review: CreateReviewSchema,
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
) -> Review:
    """Create a new review."""

    new_review = Review(
        title=review.title,
        content=review.content,
        rating=review.rating,
        book_id=review.book_id,
        user_id=current_user.id,
    )
    Review.insert(new_review, current_user.id)
    return new_review


@router.put('/{review_id}/', response_model=ReviewSchema)
async def update_review(
    review_id: int, review: UpdateReviewSchema, current_user: Annotated[UserSchema, Depends(get_current_active_user)]
) -> Review:
    """
    Update a review
    :param review_id: The id of the review
    :param review: The new data of the review
    :param current_user: The user making the request
    :return: The updated review
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    try:
        old_review = Review.find(review_id)
        updated_review = review.dict()

        Review.update(old_review, updated_review, current_user.id)

        return old_review
    except Exception as e:
        abort(400, str(e))


@router.get('/book/{book_id}/', response_model=list[ReviewSchema])
async def get_reviews_of_book(
    book_id: str,
    limit: int = None,
) -> list[Review]:
    """
    Get all reviews of a book
    :param limit: The limit of reviews to return
    :param book_id: The id of the book
    :return: A list of all the reviews of the book
    """
    return Review.list([Review.book_id == book_id, Review.disabled == false()], limit=limit)


@router.get('/user/{user_id}/', response_model=list[ReviewSchema])
async def get_reviews_of_user(
    user_id: str,
) -> list[Review]:
    """
    Get all reviews of a user
    :param user_id: The id of the user
    :return: A list of all the reviews of the user
    """
    return Review.list([Review.user_id == user_id, Review.disabled == false()])


@router.get('/friends-reviews/', response_model=list[ReviewSchema])
async def get_friends_reviews(current_user: Annotated[UserSchema, Depends(get_current_active_user)]) -> list[Review]:
    """
    Get all reviews of the friends of the current user
    :param current_user: The user making the request
    :return: A list of all the reviews of the friends of the current user
    """
    friends = User.get_friends(current_user.id)
    reviews = []
    for friend in friends:
        reviews += friend.reviews

    return reviews
