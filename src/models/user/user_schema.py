from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class UserRole(Enum):
    ADMIN = 'ADMIN'
    USER = 'USER'
    AUTHOR = 'AUTHOR'


class UserBaseSchema(BaseModel):
    """
    User base schema
    """

    id: int
    email: str
    user_role: UserRole


class UserStoredData(UserBaseSchema):
    """
    User stored data schema
    """

    username: Optional[str]


class UserBasePasswordSchema(UserBaseSchema):
    """
    User base schema with password
    """

    password: str


class UserSchema(UserBaseSchema):
    """
    User schema
    """

    name: str
    first_last_name: str
    second_last_name: Optional[str]
    date_of_birth: Optional[datetime]
    phone_number: Optional[str]
    username: Optional[str]
    full_name: str
    created_at: datetime
    modified_at: datetime
    disabled: bool

    class Config:
        """
        Config class for UserSchema
        """

        orm_mode = True

class UserProfilePicture(UserSchema):
    """
    User schema
    """

    profile_picture: Optional[str]


class CompleteUserSchema(UserSchema):
    """
    Complete user schema
    """

    profile_picture: Optional[str]


class AdminSchema(BaseModel):
    """
    Admin schema
    """

    id: int
    email: str
    name: str
    first_last_name: str
    second_last_name: Optional[str]
    username: Optional[str]


class PasswordSchema(BaseModel):
    """
    Password schema
    """

    password: str
    current_password: str
    password_confirmation: str


class UserSignUpSchema(BaseModel):
    """
    User sign up schema
    """

    email: str
    password: str
    name: str
    first_last_name: str
    date_of_birth: Optional[datetime]
    username: Optional[str]
    emerging_author: Optional[bool]
