from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import false

from src.models.user import UserSchema, UserRole, User
from src.routers.auth.auth import get_current_active_user
from src.routers.rosetta_router import create_router


api_name = 'friendship'

router = create_router(api_name)

@router.get('/{user_id}', response_model=list[UserSchema])
async def get_all_friends(user_id: int, current_user: Annotated[UserSchema, Depends(get_current_active_user)]) -> list[UserSchema]:
    """
    Get all friends of a user
    :param user_id: The id of the user
    :param current_user: The user making the request
    :return: A list of all friends of the user
    """
    friends = User.get_all_friends(user_id)

    return friends