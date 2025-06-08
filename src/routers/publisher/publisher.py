from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import false

from src.models.publisher import PublisherBaseSchema, Publisher
from src.models.user import UserSchema, UserRole
from src.routers.auth.auth import get_current_active_user
from src.routers.rosetta_router import create_router

api_name = 'publisher'

router = create_router(api_name)


@router.get('/', response_model=list[PublisherBaseSchema])
async def get_all_publishers(current_user: Annotated[UserSchema, Depends(get_current_active_user)]) -> list[Publisher]:
    """
    Get all publishers
    :param current_user: The user making the request
    :return: A list of all publishers
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    return Publisher.list([Publisher.disabled == false()], ('name', True))
