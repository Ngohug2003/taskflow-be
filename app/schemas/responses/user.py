from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


