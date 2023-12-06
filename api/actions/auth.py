from typing import Union

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import settings
from db.dao import UserDAO
from db.models import User
from db.session import get_db
from hashing import Hasher


async def get_user_by_email_for_auth(email: str, session: AsyncSession):
    async with session.begin():
        user_dal = UserDAO(session)
        return await user_dal.get_user_by_email(
            email=email,
        )


async def authenticate_user(email: str, password: str, session: AsyncSession) -> Union[User, None]:
    user = await get_user_by_email_for_auth(email=email, session=session)
    if user is None:
        return
    if not Hasher.verify_password(password, user.hashed_password):
        return
    return user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


async def get_current_user_from_token(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user_by_email_for_auth(email=email, session=session)
    if user is None:
        raise credentials_exception
    return user
