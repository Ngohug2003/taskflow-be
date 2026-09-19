from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from app.models.workspace import WorkspaceRole


class CreateWorkspaceRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Tên không gian làm việc")
    description: Optional[str] = Field(None, max_length=1000, description="Mô tả không gian làm việc")


class UpdateWorkspaceRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Tên không gian làm việc mới")
    description: Optional[str] = Field(None, max_length=1000, description="Mô tả không gian làm việc mới")


class InviteMemberRequest(BaseModel):
    email: EmailStr = Field(..., description="Email của thành viên cần mời")
    role: WorkspaceRole = Field(WorkspaceRole.MEMBER, description="Vai trò trong workspace (ADMIN hoặc MEMBER)")


class UpdateMemberRoleRequest(BaseModel):
    role: WorkspaceRole = Field(..., description="Vai trò mới trong workspace (ADMIN hoặc MEMBER)")
