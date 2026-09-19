from fastapi import APIRouter, Depends
from app.schemas.responses.user import UserResponse
from app.schemas.responses.base_response import GenericResponse
from app.services.base_service import BaseService
from app.utils.custom_log import LogRequest
from app.middlewares.auth import get_current_user
from app.models.user import User

user_router = APIRouter(route_class=LogRequest, tags=["Users"])


@user_router.get('/me', response_model=GenericResponse[UserResponse])
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Lấy thông tin tài khoản hiện tại (GET /api/v1/users/me)"""
    return BaseService.custom_response(UserResponse.model_validate(current_user))
