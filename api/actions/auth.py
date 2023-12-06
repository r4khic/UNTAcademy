from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from db.dao import UserDAO
from db.models import User
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
