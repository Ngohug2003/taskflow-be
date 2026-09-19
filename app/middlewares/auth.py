from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.constants.database import get_db
from app.repositories.user import UserRepository
from app.utils.security import decode_token
from app.models.user import User

# Sử dụng HTTPBearer thay vì OAuth2PasswordBearer để Swagger chỉ hiện ô nhập token
security = HTTPBearer()

async def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = auth.credentials
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_id_parsed = int(user_id)
    except (ValueError, TypeError):
        user_id_parsed = user_id

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id_parsed)
    if user is None or not user.is_active:
        raise credentials_exception
    return user



async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Bạn không có quyền thực hiện hành động này"
        )
    return current_user
