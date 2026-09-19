from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, model_validator
from app.models.workspace import WorkspaceRole, WorkspacePrivacy


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
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    description: Optional[str] = None
    selected_color: Optional[str] = "#2563EB"
    selectedColor: Optional[str] = "#2563EB"
    privacy: Optional[str] = "PRIVATE"
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    current_user_role: Optional[WorkspaceRole] = None
    members_count: Optional[int] = None

    @model_validator(mode="after")
    def populate_camel_case_aliases(self):
        if not self.selectedColor and self.selected_color:
            self.selectedColor = self.selected_color
        elif not self.selected_color and self.selectedColor:
            self.selected_color = self.selectedColor
        return self


class WorkspaceDetailResponse(WorkspaceResponse):
    members: List[WorkspaceMemberResponse] = []
