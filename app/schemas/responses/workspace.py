from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.workspace import WorkspaceRole


class WorkspaceMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workspace_id: int
    user_id: int
    role: WorkspaceRole
    joined_at: datetime
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    current_user_role: Optional[WorkspaceRole] = None
    members_count: Optional[int] = None


class WorkspaceDetailResponse(WorkspaceResponse):
    members: List[WorkspaceMemberResponse] = []
