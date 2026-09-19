from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.database import get_db
from app.schemas.responses.user import UserResponse
from app.schemas.responses.base_response import GenericResponse
from app.repositories.user import UserRepository
from app.middlewares.auth import require_admin
from app.services.base_service import BaseService

user_router = APIRouter(prefix="/users", dependencies=[Depends(require_admin)])

class AdminUserController(BaseService):
    @staticmethod
    async def get_list_users(db: AsyncSession, skip: int = 0, limit: int = 20):
        repo = UserRepository(db)
        users = await repo.get_all(skip=skip, limit=limit)
        return [UserResponse.model_validate(u) for u in users]

    @staticmethod
    async def get_detail(db: AsyncSession, user_id: int):
        repo = UserRepository(db)
        user = await repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.model_validate(user)

@user_router.get("", response_model=GenericResponse[List[UserResponse]])
async def list_users(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    users = await AdminUserController.get_list_users(db, skip, limit)
    return AdminUserController.custom_response(users)

@user_router.get("/{user_id}", response_model=GenericResponse[UserResponse])
async def get_user_detail(user_id: int, db: AsyncSession = Depends(get_db)):

    user = await AdminUserController.get_detail(db, user_id)
    return AdminUserController.custom_response(user)
