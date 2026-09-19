from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, AliasChoices, field_validator
from app.models.workspace import WorkspaceRole, WorkspacePrivacy


class CreateWorkspaceRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Tên không gian làm việc")
    description: Optional[str] = Field(None, max_length=1000, description="Mô tả không gian làm việc")
    selected_color: Optional[str] = Field(
        "#2563EB",
        validation_alias=AliasChoices("selectedColor", "selected_color", "color"),
        description="Màu nhận diện không gian làm việc (Hex hoặc tên màu)",
    )
    privacy: WorkspacePrivacy = Field(
        WorkspacePrivacy.PRIVATE,
        validation_alias=AliasChoices("privacy", "privacy_type"),
        description="Chế độ riêng tư (PUBLIC hoặc PRIVATE)",
    )
    invite_emails: Optional[List[EmailStr]] = Field(
        default_factory=list,
        validation_alias=AliasChoices("inviteEmails", "invite_emails", "emails"),
        description="Danh sách email mời thành viên ngay khi tạo workspace",
    )

    @field_validator("privacy", mode="before")
    @classmethod
    def normalize_privacy(cls, v):
        if isinstance(v, str):
            v_upper = v.strip().upper()
            if v_upper in WorkspacePrivacy.__members__:
                return WorkspacePrivacy(v_upper)
        return v


class UpdateWorkspaceRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Tên không gian làm việc mới")
    description: Optional[str] = Field(None, max_length=1000, description="Mô tả không gian làm việc mới")
    selected_color: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("selectedColor", "selected_color", "color"),
        description="Màu nhận diện mới",
    )
    privacy: Optional[WorkspacePrivacy] = Field(
        None,
        validation_alias=AliasChoices("privacy", "privacy_type"),
        description="Chế độ riêng tư mới (PUBLIC hoặc PRIVATE)",
    )

    @field_validator("privacy", mode="before")
    @classmethod
    def normalize_privacy(cls, v):
        if v is not None and isinstance(v, str):
            v_upper = v.strip().upper()
            if v_upper in WorkspacePrivacy.__members__:
                return WorkspacePrivacy(v_upper)
        return v


class InviteMemberRequest(BaseModel):
    email: EmailStr = Field(..., description="Email của thành viên cần mời")
    role: WorkspaceRole = Field(WorkspaceRole.MEMBER, description="Vai trò trong workspace (ADMIN hoặc MEMBER)")


class UpdateMemberRoleRequest(BaseModel):
    role: WorkspaceRole = Field(..., description="Vai trò mới trong workspace (ADMIN hoặc MEMBER)")
