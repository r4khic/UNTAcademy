from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.auth import get_current_user_from_token
from api.actions.user import create_new_user, delete_existing_user, get_existing_user_by_id, update_user
from api.models import UserCreate, ShowUser, DeleteUserResponse, UpdatedUserResponse, UpdateUserRequest
from db.models import User
from db.session import get_db

user_router = APIRouter()


@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    return await create_new_user(body, db)


@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user_from_token), ) -> DeleteUserResponse:
    deleted_user_id = await delete_existing_user(user_id, db)
    if deleted_user_id is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
    return DeleteUserResponse(deleted_user_id=deleted_user_id)


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user_from_token), ) -> ShowUser:
    user = await get_existing_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
    return user


@user_router.patch("/", response_model=UpdatedUserResponse)
async def update_user_by_id(
        user_id: UUID, body: UpdateUserRequest, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token), ) -> UpdatedUserResponse:
    updated_user_params = body.dict(exclude_none=True)
    if updated_user_params == {}:
        raise HTTPException(status_code=422, detail="At least one parameter for user update info should be provided")
    user = await get_existing_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
    updated_user_id = await update_user(updated_user_params=updated_user_params, session=db, user_id=user_id)
    return UpdatedUserResponse(updated_user_id=updated_user_id)
