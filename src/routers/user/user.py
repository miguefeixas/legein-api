from datetime import datetime, timedelta
from typing import Annotated

from fastapi import HTTPException, Depends
from sqlalchemy import false

from src.routers.auth.auth import get_current_active_user, get_password_hash, verify_password
from src.routers.rosetta_router import create_router
from src.models.user import UserSchema, UserRole, UserBaseSchema, User, AdminSchema, PasswordSchema, CompleteUserSchema, \
    UserProfilePicture
from src.utils.schemas.kpi_schema import create_kpi_schema

api_name = 'user'

router = create_router(api_name)


@router.get('/', response_model=list[UserSchema])
async def get_all_users(current_user: Annotated[UserSchema, Depends(get_current_active_user)]) -> list[User]:
    """
    Get all users
    :param current_user: The user making the request
    :return: A list of all users
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    return User.list_first_pending()


@router.get('/{user_id}', response_model=UserSchema)
async def get_user(user_id: int, current_user: Annotated[UserSchema, Depends(get_current_active_user)]) -> User:
    """
    Get user by id
    :param user_id: Id of the user to get
    :param current_user: The user making the request
    :return: The user with the given id
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    user = User.find(user_id)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail='User not found')


@router.get('/get-hash/{password}', response_model=str)
async def get_hash(password: str) -> str:
    """
    Get the hash of a password
    :param password: The password to hash
    :return: The hashed password
    """
    return get_password_hash(password)


@router.get('/users-last-seven-days/', response_model=create_kpi_schema(UserBaseSchema))
async def get_last_seven_days_users(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)]
) -> dict[str, int | list[User]]:
    """
    Get the list of the users created in the last seven days
    :param current_user: The user making the request
    :return: The list of users created in the last seven days
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    fourteen_days_ago = today - timedelta(days=14)

    users_this_week = User.list(
        [
            User.created_at <= today,
            User.created_at >= seven_days_ago,
            User.user_role == UserRole.USER.value,
            User.disabled == false(),
        ]
    )

    total_past_week = User.list(
        [
            User.created_at <= seven_days_ago,
            User.created_at >= fourteen_days_ago,
            User.user_role == UserRole.USER.value,
            User.disabled == false(),
        ]
    )

    return {'total_past_week': len(total_past_week), 'this_week': users_this_week}


@router.get('/emerging-last-seven-days/', response_model=create_kpi_schema(UserBaseSchema))
async def get_last_seven_days_emerging(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)]
) -> dict[str, int | list[User]]:
    """
    Get the list of the emerging authors created in the last seven days
    :param current_user: The user making the request
    :return: The list of emerging authors created in the last seven days
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    fourteen_days_ago = today - timedelta(days=14)

    emerging_authors_this_week = User.list(
        [
            User.created_at <= today,
            User.created_at >= seven_days_ago,
            User.user_role == UserRole.AUTHOR.value,
            User.disabled == false(),
        ]
    )

    total_past_week = User.list(
        [
            User.created_at <= seven_days_ago,
            User.created_at >= fourteen_days_ago,
            User.user_role == UserRole.AUTHOR.value,
            User.disabled == false(),
        ]
    )

    return {'total_past_week': len(total_past_week), 'this_week': emerging_authors_this_week}


@router.patch('/admin/{admin_id}', response_model=UserSchema)
async def update_admin(
    admin_id: int,
    user: AdminSchema,
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
) -> UserSchema:
    """
    Update admin by id
    :param admin_id: Id of the admin to update
    :param user: The new admin data
    :param current_user: The user making the request
    :return: The updated user
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')
    if current_user.id != admin_id:
        raise HTTPException(status_code=401, detail='Cannot update this user')

    user_to_update = User.find(admin_id)
    updated_data = user.dict()
    if user_to_update:
        user_to_update.update(updated_data, current_user.id)
        return user_to_update
    else:
        raise HTTPException(status_code=404, detail='User not found')


@router.patch('/admin/password/{admin_id}', response_model=None, status_code=204)
async def update_admin_password(
    admin_id: int,
    data: PasswordSchema,
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
) -> None:
    """
    Update admin password by id
    :param admin_id: Id of the admin to update
    :param data: The new password data
    :param current_user: The user making the request
    :return: The updated user
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')
    if current_user.id != admin_id:
        raise HTTPException(status_code=401, detail='Cannot update this user')

    user_to_update = User.find(admin_id)
    if user_to_update and verify_password(data.current_password, user_to_update.password):
        user_to_update.update({'password': get_password_hash(data.password)}, current_user.id)
    else:
        raise HTTPException(status_code=404, detail='API.ERROR.WRONGPASSWORD')


@router.get('/{user_id}/profile/', response_model=CompleteUserSchema)
async def get_user(user_id: int, current_user: Annotated[UserSchema, Depends(get_current_active_user)]) -> User:
    """
    Get user by id
    :param user_id: Id of the user to get
    :param current_user: The user making the request
    :return: The user with the given id
    """
    if current_user.id != user_id and current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    user = User.find(user_id)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail='User not found')


@router.patch('/user/{user_id}', response_model=UserProfilePicture)
async def update_admin(
    user_id: int,
    user: UserProfilePicture,
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
) -> UserSchema:
    """
    Update admin by id
    :param user_id: Id of the user to update
    :param user: The new user data
    :param current_user: The user making the request
    :return: The updated user
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=401, detail='Cannot update this user')

    user_to_update = User.find(user_id)
    updated_data = user.dict()
    updated_data.pop('full_name')
    if user_to_update:
        user_to_update.update(updated_data, current_user.id)
        return user_to_update
    else:
        raise HTTPException(status_code=404, detail='User not found')


@router.put('/{user_id}/activate')
async def activate_user(
    user_id: int,
    current_user: Annotated[UserSchema, Depends(get_current_active_user)]
) -> None:
    """
    Activate a user by id
    :param user_id: Id of the user to activate
    :param current_user: The user making the request
    :return: The activated user
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    user = User.find(user_id)
    if user:
        user.update({'disabled': False}, current_user.id)
    else:
        raise HTTPException(status_code=404, detail='User not found')

@router.put('/{user_id}/deactivate')
async def deactivate_user(
    user_id: int,
    current_user: Annotated[UserSchema, Depends(get_current_active_user)]
) -> None:
    """
    Deactivate a user by id
    :param user_id: Id of the user to deactivate
    :param current_user: The user making the request
    :return: The deactivated user
    """
    if current_user.user_role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    user = User.find(user_id)
    if user:
        user.update({'disabled': True}, current_user.id)
    else:
        raise HTTPException(status_code=404, detail='User not found')

@router.delete('/{user_id}')
async def delete_user(
    user_id: int,
    current_user: Annotated[UserSchema, Depends(get_current_active_user)]
) -> None:
    """
    Delete a user by id
    :param user_id: Id of the user to delete
    :param current_user: The user making the request
    :return: None
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    user = User.find(user_id)
    if user:
        user.delete()
    else:
        raise HTTPException(status_code=404, detail='User not found')
