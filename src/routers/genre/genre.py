from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import false

from src.models.genre import GenreBaseSchema, Genre
from src.models.user import UserSchema, UserRole
from src.routers.auth.auth import get_current_active_user
from src.routers.rosetta_router import create_router


api_name = 'genre'

router = create_router(api_name)


@router.get('/', response_model=list[GenreBaseSchema])
async def get_all_genres(current_user: Annotated[UserSchema, Depends(get_current_active_user)]) -> list[Genre]:
    """
    Get all genres
    :param current_user: The user making the request
    :return: A list of all genres
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    return Genre.list([Genre.disabled == false()], ('name', True))
