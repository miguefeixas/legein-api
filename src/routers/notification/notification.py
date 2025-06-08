from typing import Annotated

from fastapi import Depends, HTTPException

from src.models.notification import Notification, NotificationSchema
from src.models.user import UserSchema
from src.routers.auth.auth import get_current_active_user
from src.routers.rosetta_router import create_router

api_name = 'notification'

router = create_router(api_name)

@router.get('/{user_id}', response_model=list[NotificationSchema])
async def get_notifications_of_user(
    user_id: int, current_user: Annotated[UserSchema, Depends(get_current_active_user)]
) -> list[Notification]:
    """
    Get a review by its id
    :param user_id: The id of the user
    :param current_user: The user making the request
    :return: The review with the given id
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    return Notification.list([Notification.user_id == user_id])

