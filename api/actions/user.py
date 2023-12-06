from typing import Union
from uuid import UUID

from api.models import ShowUser, UserCreate
from db.dao import UserDAO
from hashing import Hasher


async def create_new_user(body: UserCreate, session) -> ShowUser:
    async with session.begin():
        user_dal = UserDAO(session)
        user = await user_dal.create_user(
            name=body.name,
            surname=body.surname,
            email=body.email,
            hashed_password=Hasher.get_password_hash(body.password),
        )
        return ShowUser(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
        )


async def delete_existing_user(user_id, session) -> Union[UUID, None]:
    async with session.begin():
        user_dal = UserDAO(session)
        deleted_user_id = await user_dal.delete_user(
            user_id=user_id,
        )
        return deleted_user_id


async def update_user(updated_user_params: dict, user_id: UUID, session) -> Union[UUID, None]:
    async with session.begin():
        user_dal = UserDAO(session)
        updated_user_id = await user_dal.update_user(
            user_id=user_id,
            **updated_user_params
        )
        return updated_user_id


async def get_existing_user_by_id(user_id, session) -> Union[ShowUser, None]:
    async with session.begin():
        user_dal = UserDAO(session)
        user = await user_dal.get_user_by_id(
            user_id=user_id,
        )
        if user is not None:
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            )
