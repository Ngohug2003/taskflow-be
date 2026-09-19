from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.database import get_db
from app.middlewares.auth import get_current_user
from app.models.user import User
from app.schemas.requests.workspace import (
    CreateWorkspaceRequest,
    UpdateWorkspaceRequest,
    InviteMemberRequest,
    UpdateMemberRoleRequest,
)
from app.schemas.responses.workspace import (
    WorkspaceResponse,
    WorkspaceDetailResponse,
    WorkspaceMemberResponse,
)
from app.schemas.responses.base_response import GenericResponse
from app.services.base_service import BaseService
from app.services.workspace_service import WorkspaceService
from app.utils.custom_log import LogRequest

workspace_router = APIRouter(route_class=LogRequest, tags=["Workspaces"])


@workspace_router.get('', response_model=GenericResponse[List[WorkspaceResponse]])
async def list_workspaces(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy danh sách các Không gian làm việc (Workspace) mà người dùng hiện tại tham gia"""
    data = await WorkspaceService.list_user_workspaces(db, current_user)
    return BaseService.custom_response(data)


@workspace_router.post('', response_model=GenericResponse[WorkspaceResponse], status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: CreateWorkspaceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Tạo không gian làm việc mới (Người tạo tự động trở thành OWNER)"""
    data = await WorkspaceService.create_workspace(db, current_user, payload)
    return BaseService.custom_response(data, status_code=status.HTTP_201_CREATED)


@workspace_router.get('/{workspace_id}', response_model=GenericResponse[WorkspaceDetailResponse])
async def get_workspace_detail(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy thông tin chi tiết Workspace kèm danh sách thành viên (Yêu cầu phải là thành viên)"""
    data = await WorkspaceService.get_workspace_detail(db, current_user, workspace_id)
    return BaseService.custom_response(data)


@workspace_router.patch('/{workspace_id}', response_model=GenericResponse[WorkspaceResponse])
async def update_workspace(
    workspace_id: int,
    payload: UpdateWorkspaceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Chỉnh sửa thông tin Workspace (Yêu cầu quyền OWNER hoặc ADMIN)"""
    data = await WorkspaceService.update_workspace(db, current_user, workspace_id, payload)
    return BaseService.custom_response(data)


@workspace_router.delete('/{workspace_id}', response_model=GenericResponse[dict])
async def delete_workspace(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Xóa vĩnh viễn Workspace (Chỉ duy nhất OWNER)"""
    await WorkspaceService.delete_workspace(db, current_user, workspace_id)
    return BaseService.custom_response({"message": "Đã xóa không gian làm việc thành công"})


@workspace_router.get('/{workspace_id}/members', response_model=GenericResponse[List[WorkspaceMemberResponse]])
async def list_workspace_members(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy danh sách thành viên trong Workspace (Yêu cầu phải là thành viên)"""
    data = await WorkspaceService.get_members(db, current_user, workspace_id)
    return BaseService.custom_response(data)


@workspace_router.post(
    '/{workspace_id}/members/invite',
    response_model=GenericResponse[WorkspaceMemberResponse],
    status_code=status.HTTP_201_CREATED,
)
async def invite_member(
    workspace_id: int,
    payload: InviteMemberRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Thêm hoặc mời thành viên vào Workspace qua email (Yêu cầu OWNER hoặc ADMIN)"""
    data = await WorkspaceService.invite_member(db, current_user, workspace_id, payload)
    return BaseService.custom_response(data, status_code=status.HTTP_201_CREATED)


@workspace_router.patch(
    '/{workspace_id}/members/{target_user_id}',
    response_model=GenericResponse[WorkspaceMemberResponse],
)
async def update_member_role(
    workspace_id: int,
    target_user_id: int,
    payload: UpdateMemberRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cập nhật vai trò của thành viên trong Workspace (Chỉ duy nhất OWNER)"""
    data = await WorkspaceService.update_member_role(db, current_user, workspace_id, target_user_id, payload)
    return BaseService.custom_response(data)


@workspace_router.delete('/{workspace_id}/members/{target_user_id}', response_model=GenericResponse[dict])
async def remove_member(
    workspace_id: int,
    target_user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Xóa thành viên khỏi Workspace hoặc thành viên tự rời khỏi Workspace"""
    await WorkspaceService.remove_member(db, current_user, workspace_id, target_user_id)
    return BaseService.custom_response({"message": "Thành viên đã được gỡ khỏi không gian làm việc thành công"})
