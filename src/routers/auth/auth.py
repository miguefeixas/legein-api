from datetime import datetime, timezone, timedelta
from typing import Annotated

import toml
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from werkzeug.exceptions import abort

from src.models.access_token import AccessToken
from src.routers.rosetta_router import create_router
from src.models.user import UserSchema, UserBasePasswordSchema, UserStoredData, UserSignUpSchema, UserRole
from src.models.user.user import User
from passlib.context import CryptContext
from jose import JWTError, jwt

with open('./configs/.secrets.local.toml', 'r') as f:
    config = toml.load(f)

api_name = 'auth'

router = create_router(api_name)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/token')

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

SECRET_KEY = config['auth']['SECRET_KEY']
ALGORITHM = config['auth']['ALGORITHM']
ACCESS_TOKEN_EXPIRE_DAYS = config['auth']['ACCESS_TOKEN_EXPIRE_DAYS']


class Token(BaseModel):
    """
    Token model
    """

    access_token: str
    token_type: str


class LoginResponse(Token):
    """
    Login response model
    """

    user: UserStoredData


class TokenData(BaseModel):
    """
    Token data model
    """

    user_id: int | None = None


def verify_password(plain_password, hashed_password):
    """
    Verify a hashed password
    :param plain_password:
    :param hashed_password:
    :return:
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Generates a hash for a password
    :param password:
    :return:
    """
    return pwd_context.hash(password)


def get_user(users, email: str) -> UserBasePasswordSchema | None:
    """
    Get user by id
    :param users:
    :param email:
    """
    for user in users:
        if email in user.email:
            user_dict = user
            return UserBasePasswordSchema(**(user_dict.to_dict()))

    return None


def authenticate_user(users, email: str, password: str) -> UserBasePasswordSchema | bool:
    """
    Authenticate user
    :param users:
    :param email:
    :param password:
    :return:
    """
    user = get_user(users, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Creates a JWT access token
    :param data:
    :param expires_delta:
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    Get current user
    :param token:
    :return:
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get('sub')
        if user_id is None:
            raise credentials_exception

        stored_token = AccessToken.find(token)
        # if stored_token is None or not stored_token.valid:
        #     raise credentials_exception

        token_data = TokenData(user_id=user_id)
    except JWTError as e:
        raise e
    user = User.find(token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserBasePasswordSchema, Depends(get_current_user)],
) -> UserBasePasswordSchema:
    """
    Get the current user if is active
    :param current_user:
    :return:
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


@router.get('/current-user')
async def get_current_user(current_user: Annotated[UserSchema, Depends(get_current_active_user)]) -> UserSchema:
    """
    Endpoint to get current user
    :param current_user:
    :return:
    """
    return current_user


@router.post('/login')
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> LoginResponse:
    """
    Login endpoint using JWT and OAuth2
    :param form_data:
    :return:
    """
    users = User.list()
    user_logged = authenticate_user(users, form_data.username, form_data.password)
    if not user_logged:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    user = User.find(user_logged.id)

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Inactive user',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(data={'sub': str(user_logged.id)}, expires_delta=access_token_expires)
    AccessToken.insert(access_token, True, datetime.now(timezone.utc) + access_token_expires)
    user = User.find(user_logged.id)
    user_stored = UserStoredData(**(user.to_dict()))
    return LoginResponse(access_token=access_token, token_type='bearer', user=user_stored)  # noqa S106


@router.get('/logout')
async def logout(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """
    Logout endpoint
    :return:
    """
    AccessToken.invalid(token)
    return {'message': 'Logged out'}


@router.post('/token')
async def login_for_access_token_swagger(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    Endpoint for swagger login
    :param form_data:
    :return:
    """
    users = User.list()
    user = authenticate_user(users, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(data={'sub': str(user.id)}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type='bearer')  # noqa S106


@router.post('/signup', response_model=UserSchema)
async def signup(user: UserSignUpSchema) -> User:
    """
    Signup endpoint
    :param user:
    :return user:
    """
    existing_email = User.find_by([User.email == user.email])
    existing_username = User.find_by([User.username == user.username])
    if existing_email:
        raise HTTPException(status_code=400, detail={'message': 'Username already exists', 'error_code': 'API.ERROR.ALREADYEXISTSEMAIL'})
    if existing_username:
        raise HTTPException(status_code=400, detail={'message': 'Username already exists', 'error_code': 'API.ERROR.ALREADYEXISTSUSERNAME'})

    new_user = User()
    tz = timezone.utc
    user.date_of_birth = user.date_of_birth.astimezone()
    user.date_of_birth = user.date_of_birth.replace(tzinfo=tz)
    new_user.add_from_dict(user.dict())
    new_user.password = get_password_hash(user.password)
    new_user.user_role = UserRole.USER if not user.emerging_author else UserRole.AUTHOR
    User.insert(new_user, None)

    if new_user.user_role == UserRole.AUTHOR:
        from src.models.author import Author

        author = Author()
        author.name = new_user.name
        author.first_last_name = new_user.first_last_name
        author.date_of_birth = new_user.date_of_birth
        try:
            new_author = Author.insert(author, None)

            new_user.author_id = new_author.id
            User.update(new_user, {'author_id': new_author.id}, None)
        except Exception as e:
            new_user.delete()
            raise HTTPException(status_code=500, detail=f'An error occurred while creating the author: {str(e)}') from None

    return new_user


@router.get('/check-email/{email}', response_model=bool)
async def check_email(email: str) -> bool:
    """
    Check if email exists
    :param email:
    :return:
    """
    existing_email = User.find_by([User.email == email])
    return existing_email is None


@router.get('/check-username/{username}', response_model=bool)
async def check_username(username: str) -> bool:
    """
    Check if username exists
    :param username:
    :return:
    """
    existing_username = User.find_by([User.username == username])
    return existing_username is None
