from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.database import get_db
from app.schemas.requests.auth import (
    LoginRequest,
    RegisterRequest,
    GoogleAuthRequest,
    RefreshTokenRequest,
)
from app.schemas.responses.user import UserResponse
from app.schemas.responses.auth import TokenResponse
from app.schemas.responses.base_response import GenericResponse
from app.services.auth_service import AuthService
from app.services.base_service import BaseService
from app.utils.custom_log import LogRequest
from app.middlewares.auth import get_current_user
from app.models.user import User

# Sử dụng route_class=LogRequest để tự động ghi log mọi request
auth_router = APIRouter(route_class=LogRequest, tags=["Authentication"])


@auth_router.post('/register', response_model=GenericResponse[TokenResponse], status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Đăng ký tài khoản mới bằng Email và Mật khẩu"""
    token_data = await AuthService.register(db, payload)
    return BaseService.custom_response(
        TokenResponse.model_validate(token_data),
        status_code=status.HTTP_201_CREATED
    )



@auth_router.post('/login', response_model=GenericResponse[TokenResponse])
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Đăng nhập hệ thống bằng Email và Mật khẩu"""
    token_data = await AuthService.login(db, payload)
    return BaseService.custom_response(TokenResponse.model_validate(token_data))


@auth_router.post('/google', response_model=GenericResponse[TokenResponse])
async def google_auth(payload: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    """Đăng nhập hoặc đăng ký nhanh bằng tài khoản Google (Google ID Token)"""
    token_data = await AuthService.google_auth(db, payload.credential)
    return BaseService.custom_response(TokenResponse.model_validate(token_data))


@auth_router.post('/refresh', response_model=GenericResponse[TokenResponse])
async def refresh_token(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Làm mới Access Token & xoay vòng Refresh Token (Token Rotation)"""
    token_data = await AuthService.refresh_token(db, payload.refresh_token)
    return BaseService.custom_response(TokenResponse.model_validate(token_data))


@auth_router.post('/logout', response_model=GenericResponse[dict])
async def logout(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Đăng xuất và thu hồi Refresh Token"""
    await AuthService.logout(db, payload.refresh_token)
    return BaseService.custom_response({"message": "Đăng xuất thành công"})

