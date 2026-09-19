from datetime import datetime, timezone
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.requests.auth import LoginRequest, RegisterRequest
from app.services.base_service import BaseService
from app.utils.custom_exception import CustomException
from app.repositories.user import UserRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_refresh_token,
    hash_token,
    get_refresh_token_expiry,
)
from app.utils.configs import project_settings as settings


class AuthService(BaseService):

    @classmethod
    async def _issue_token_pair(cls, db_session: AsyncSession, user: User) -> dict:
        """Helper cấp cặp Access Token + Refresh Token và lưu Refresh Token vào Database"""
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        raw_refresh_token = generate_refresh_token()
        token_hashed = hash_token(raw_refresh_token)

        refresh_repo = RefreshTokenRepository(db_session)
        new_refresh = RefreshToken(
            user_id=user.id,
            token_hash=token_hashed,
            expires_at=get_refresh_token_expiry(),
        )
        await refresh_repo.create(new_refresh)

        return {
            "access_token": access_token,
            "refresh_token": raw_refresh_token,
            "token_type": "bearer",
            "user": user,
        }

    @classmethod
    async def register(cls, db_session: AsyncSession, request_data: RegisterRequest) -> dict:
        """Đăng ký tài khoản mới bằng Email + Password"""
        repo = UserRepository(db_session)
        email = request_data.email.lower().strip()
        existing_user = await repo.get_by_email(email)
        if existing_user:
            raise CustomException(400, "Email đã được sử dụng. Vui lòng chọn email khác hoặc đăng nhập.")

        name = request_data.name.strip()

        new_user = User(
            email=email,
            name=name,
            hashed_password=hash_password(request_data.password),
            is_active=True,
            is_admin=False,
        )
        created_user = await repo.create(new_user)
        return await cls._issue_token_pair(db_session, created_user)

    @classmethod
    async def login(cls, db_session: AsyncSession, request_data: LoginRequest) -> dict:
        """Đăng nhập bằng Email + Password"""
        repo = UserRepository(db_session)
        email = request_data.email.lower().strip()
        user = await repo.get_by_email(email)

        if not user or not verify_password(request_data.password, user.hashed_password):
            raise CustomException(401, "Email hoặc mật khẩu không chính xác.")

        if not user.is_active:
            raise CustomException(403, "Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ quản trị viên.")

        return await cls._issue_token_pair(db_session, user)

    @classmethod
    async def google_auth(cls, db_session: AsyncSession, credential: str) -> dict:
        """Xác thực Google ID Token và đăng nhập / đăng ký tài khoản Google"""
        if not credential or not credential.strip():
            raise CustomException(400, "Thiếu Google credential token.")

        # Xác thực trực tiếp với Google (hỗ trợ cả ID Token và Access Token)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if credential.startswith("ya29."):
                    # Google OAuth2 Access Token (từ useGoogleLogin)
                    response = await client.get(
                        "https://www.googleapis.com/oauth2/v3/userinfo",
                        headers={"Authorization": f"Bearer {credential}"}
                    )
                else:
                    # Google ID Token (từ GoogleLogin component hoặc One Tap)
                    response = await client.get(
                        f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}"
                    )
        except Exception as e:
            raise CustomException(502, f"Không thể kết nối đến máy chủ xác thực Google: {str(e)}")


        if response.status_code != 200:
            raise CustomException(401, "Google token không hợp lệ hoặc đã hết hạn.")

        google_data = response.json()
        google_id = google_data.get("sub")
        email = google_data.get("email", "").lower().strip()
        name = google_data.get("name") or google_data.get("given_name") or email.split("@")[0]
        avatar_url = google_data.get("picture")

        if not email or not google_id:
            raise CustomException(400, "Google token không chứa email hoặc định danh người dùng.")

        # Kiểm tra AUD nếu google_data có chứa trường aud và GOOGLE_CLIENT_ID được cấu hình
        token_aud = google_data.get("aud")
        if token_aud and settings.GOOGLE_CLIENT_ID and token_aud != settings.GOOGLE_CLIENT_ID:
            raise CustomException(401, "Google Client ID không khớp với cấu hình hệ thống.")


        repo = UserRepository(db_session)
        # 1. Tìm theo google_id
        user = await repo.get_by_google_id(google_id)

        if not user:
            # 2. Tìm theo email để liên kết nếu đã đăng ký email trước đó
            user = await repo.get_by_email(email)
            if user:
                user.google_id = google_id
                if not user.avatar_url and avatar_url:
                    user.avatar_url = avatar_url
                if not user.name and name:
                    user.name = name
                await repo.update(user)
            else:
                # 3. Tạo tài khoản mới từ Google
                new_user = User(
                    email=email,
                    name=name,
                    google_id=google_id,
                    avatar_url=avatar_url,
                    hashed_password=None,
                    is_active=True,
                    is_admin=False,
                )
                user = await repo.create(new_user)

        if not user.is_active:
            raise CustomException(403, "Tài khoản của bạn đã bị vô hiệu hóa.")

        return await cls._issue_token_pair(db_session, user)

    @classmethod
    async def refresh_token(cls, db_session: AsyncSession, refresh_token_str: str) -> dict:
        """Làm mới Access Token & xoay vòng Refresh Token (Token Rotation)"""
        if not refresh_token_str:
            raise CustomException(400, "Thiếu refresh token.")

        token_hashed = hash_token(refresh_token_str)
        refresh_repo = RefreshTokenRepository(db_session)
        token_record = await refresh_repo.get_by_token_hash(token_hashed)

        if not token_record or token_record.revoked_at is not None:
            raise CustomException(401, "Refresh token không hợp lệ hoặc đã bị thu hồi.")

        now_utc = datetime.now(timezone.utc)
        if token_record.expires_at < now_utc:
            raise CustomException(401, "Refresh token đã hết hạn. Vui lòng đăng nhập lại.")

        user_repo = UserRepository(db_session)
        user = await user_repo.get_by_id(token_record.user_id)
        if not user or not user.is_active:
            raise CustomException(401, "Tài khoản không tồn tại hoặc đã bị khóa.")

        # Thu hồi token cũ (Token Rotation để ngăn ngừa token replay attack)
        await refresh_repo.revoke_token(token_hashed)

        # Cấp cặp token mới
        new_access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        new_raw_refresh = generate_refresh_token()
        new_token_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_raw_refresh),
            expires_at=get_refresh_token_expiry(),
        )
        await refresh_repo.create(new_token_record)

        return {
            "access_token": new_access_token,
            "refresh_token": new_raw_refresh,
            "token_type": "bearer",
            "user": user,
        }

    @classmethod
    async def logout(cls, db_session: AsyncSession, refresh_token_str: str) -> bool:
        """Đăng xuất và thu hồi Refresh Token"""
        if refresh_token_str:
            token_hashed = hash_token(refresh_token_str)
            refresh_repo = RefreshTokenRepository(db_session)
            await refresh_repo.revoke_token(token_hashed)
        return True
