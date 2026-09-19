from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.utils.configs import project_settings
from app.utils.custom_exception import CustomException
from app.constants.database import get_db as get_db_session
from app.middlewares.auth import get_current_user
from app.models.user import User

class CheckPermission:
    def __init__(self, required_admin: bool = False):
        self.required_admin = required_admin

    async def __call__(self, current_user: User = Depends(get_current_user)):
        if self.required_admin and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền thực hiện hành động này"
            )
        return {
            "user_id": current_user.id,
            "email": current_user.email,
            "is_admin": current_user.is_admin
        }