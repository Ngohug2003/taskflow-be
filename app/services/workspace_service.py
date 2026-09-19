from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole
from app.repositories.workspace import WorkspaceRepository
from app.repositories.workspace_member import WorkspaceMemberRepository
from app.repositories.user import UserRepository
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
from app.utils.custom_exception import CustomException


class WorkspaceService:
    @staticmethod
    def _map_member_response(member: WorkspaceMember) -> WorkspaceMemberResponse:
        user = member.user
        return WorkspaceMemberResponse(
            id=member.id,
            workspace_id=member.workspace_id,
            user_id=member.user_id,
            role=member.role,
            joined_at=member.joined_at,
            name=user.name if user else None,
            email=user.email if user else "",
            avatar_url=user.avatar_url if user else None,
        )

    @classmethod
    async def create_workspace(
        cls, db: AsyncSession, current_user: User, payload: CreateWorkspaceRequest
    ) -> WorkspaceResponse:
        """Tạo workspace mới và tự động gán user tạo thành OWNER (BR-WS-001)"""
        workspace_repo = WorkspaceRepository(db)
        member_repo = WorkspaceMemberRepository(db)

        # 1. Tạo Workspace
        workspace = Workspace(
            name=payload.name.strip(),
            description=payload.description.strip() if payload.description else None,
            owner_id=current_user.id,
        )
        await workspace_repo.create(workspace)

        # 2. Tự động thêm owner vào bảng workspace_members với role OWNER
        owner_member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=current_user.id,
            role=WorkspaceRole.OWNER,
        )
        await member_repo.create(owner_member)

        return WorkspaceResponse(
            id=workspace.id,
            name=workspace.name,
            description=workspace.description,
            owner_id=workspace.owner_id,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at,
            current_user_role=WorkspaceRole.OWNER,
            members_count=1,
        )

    @classmethod
    async def list_user_workspaces(
        cls, db: AsyncSession, current_user: User
    ) -> List[WorkspaceResponse]:
        """Lấy tất cả workspace mà user đang tham gia kèm role tương ứng"""
        workspace_repo = WorkspaceRepository(db)
        items = await workspace_repo.get_workspaces_for_user(current_user.id)

        response_list: List[WorkspaceResponse] = []
        for ws, membership in items:
            count = await workspace_repo.count_members(ws.id)
            response_list.append(
                WorkspaceResponse(
                    id=ws.id,
                    name=ws.name,
                    description=ws.description,
                    owner_id=ws.owner_id,
                    created_at=ws.created_at,
                    updated_at=ws.updated_at,
                    current_user_role=membership.role,
                    members_count=count,
                )
            )
        return response_list

    @classmethod
    async def get_workspace_detail(
        cls, db: AsyncSession, current_user: User, workspace_id: int
    ) -> WorkspaceDetailResponse:
        """Lấy chi tiết workspace và danh sách thành viên (BR-WS-003)"""
        workspace_repo = WorkspaceRepository(db)
        member_repo = WorkspaceMemberRepository(db)

        # Kiểm tra quyền truy cập: Phải là thành viên của Workspace
        caller_membership = await member_repo.get_member(workspace_id, current_user.id)
        if not caller_membership:
            raise CustomException(403, "Bạn không phải là thành viên của không gian làm việc này.")

        ws = await workspace_repo.get_with_members(workspace_id)
        if not ws:
            raise CustomException(404, "Không tìm thấy không gian làm việc.")

        members_dto = [cls._map_member_response(m) for m in ws.members]
        return WorkspaceDetailResponse(
            id=ws.id,
            name=ws.name,
            description=ws.description,
            owner_id=ws.owner_id,
            created_at=ws.created_at,
            updated_at=ws.updated_at,
            current_user_role=caller_membership.role,
            members_count=len(members_dto),
            members=members_dto,
        )

    @classmethod
    async def update_workspace(
        cls, db: AsyncSession, current_user: User, workspace_id: int, payload: UpdateWorkspaceRequest
    ) -> WorkspaceResponse:
        """Chỉnh sửa thông tin workspace (Chỉ OWNER hoặc ADMIN)"""
        workspace_repo = WorkspaceRepository(db)
        member_repo = WorkspaceMemberRepository(db)

        caller_membership = await member_repo.get_member(workspace_id, current_user.id)
        if not caller_membership:
            raise CustomException(403, "Bạn không có quyền truy cập không gian làm việc này.")

        if caller_membership.role not in [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]:
            raise CustomException(403, "Chỉ Quản trị viên hoặc Chủ sở hữu mới có quyền chỉnh sửa workspace.")

        ws = await workspace_repo.get_by_id(workspace_id)
        if not ws:
            raise CustomException(404, "Không tìm thấy không gian làm việc.")

        if payload.name is not None:
            ws.name = payload.name.strip()
        if payload.description is not None:
            ws.description = payload.description.strip() if payload.description else None

        await workspace_repo.update(ws)
        count = await workspace_repo.count_members(ws.id)

        return WorkspaceResponse(
            id=ws.id,
            name=ws.name,
            description=ws.description,
            owner_id=ws.owner_id,
            created_at=ws.created_at,
            updated_at=ws.updated_at,
            current_user_role=caller_membership.role,
            members_count=count,
        )

    @classmethod
    async def delete_workspace(
        cls, db: AsyncSession, current_user: User, workspace_id: int
    ) -> None:
        """Xóa vĩnh viễn workspace (Chỉ duy nhất OWNER - BR-WS-005)"""
        workspace_repo = WorkspaceRepository(db)
        ws = await workspace_repo.get_by_id(workspace_id)
        if not ws:
            raise CustomException(404, "Không tìm thấy không gian làm việc.")

        if ws.owner_id != current_user.id:
            raise CustomException(403, "Chỉ Chủ sở hữu (Owner) mới có quyền xóa không gian làm việc này.")

        await workspace_repo.delete(ws)

    @classmethod
    async def get_members(
        cls, db: AsyncSession, current_user: User, workspace_id: int
    ) -> List[WorkspaceMemberResponse]:
        """Lấy danh sách thành viên trong workspace"""
        member_repo = WorkspaceMemberRepository(db)
        caller_membership = await member_repo.get_member(workspace_id, current_user.id)
        if not caller_membership:
            raise CustomException(403, "Bạn không có quyền xem thành viên của không gian làm việc này.")

        members = await member_repo.get_members_by_workspace(workspace_id)
        return [cls._map_member_response(m) for m in members]

    @classmethod
    async def invite_member(
        cls, db: AsyncSession, current_user: User, workspace_id: int, payload: InviteMemberRequest
    ) -> WorkspaceMemberResponse:
        """Mời/Thêm thành viên vào workspace qua email (BR-WS-004)"""
        workspace_repo = WorkspaceRepository(db)
        member_repo = WorkspaceMemberRepository(db)
        user_repo = UserRepository(db)

        # 1. Kiểm tra quyền của caller
        caller_membership = await member_repo.get_member(workspace_id, current_user.id)
        if not caller_membership or caller_membership.role not in [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]:
            raise CustomException(403, "Chỉ Chủ sở hữu hoặc Quản trị viên mới có quyền mời thành viên.")

        ws = await workspace_repo.get_by_id(workspace_id)
        if not ws:
            raise CustomException(404, "Không tìm thấy không gian làm việc.")

        # 2. Không được mời với vai trò OWNER (BR-WS-001)
        if payload.role == WorkspaceRole.OWNER:
            raise CustomException(400, "Không thể gán vai trò Chủ sở hữu khi mời thành viên mới.")

        # 3. Tìm tài khoản người dùng theo email
        clean_email = payload.email.lower().strip()
        target_user = await user_repo.get_by_email(clean_email)
        if not target_user:
            raise CustomException(
                404, f"Không tìm thấy tài khoản với email '{clean_email}'. Người dùng cần đăng ký trước khi được mời."
            )

        # 4. Kiểm tra xem người dùng đã là thành viên chưa
        existing_member = await member_repo.get_member(workspace_id, target_user.id)
        if existing_member:
            raise CustomException(400, "Người dùng này đã là thành viên của không gian làm việc.")

        # 5. Thêm bản ghi thành viên mới
        new_member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=target_user.id,
            role=payload.role,
        )
        await member_repo.create(new_member)
        new_member.user = target_user

        return cls._map_member_response(new_member)

    @classmethod
    async def update_member_role(
        cls, db: AsyncSession, current_user: User, workspace_id: int, target_user_id: int, payload: UpdateMemberRoleRequest
    ) -> WorkspaceMemberResponse:
        """Cập nhật vai trò thành viên (Chỉ duy nhất OWNER mới có quyền chuyển đổi ADMIN <-> MEMBER)"""
        member_repo = WorkspaceMemberRepository(db)

        # 1. Caller phải là OWNER
        caller_membership = await member_repo.get_member(workspace_id, current_user.id)
        if not caller_membership or caller_membership.role != WorkspaceRole.OWNER:
            raise CustomException(403, "Chỉ Chủ sở hữu mới có quyền thay đổi vai trò của thành viên.")

        # 2. Tìm thành viên cần đổi
        target_member = await member_repo.get_member(workspace_id, target_user_id)
        if not target_member:
            raise CustomException(404, "Không tìm thấy thành viên này trong workspace.")

        # 3. Không thể tự thay đổi vai trò của OWNER
        if target_member.role == WorkspaceRole.OWNER:
            raise CustomException(400, "Không thể thay đổi vai trò của Chủ sở hữu.")

        if payload.role == WorkspaceRole.OWNER:
            raise CustomException(400, "Không thể thăng cấp thành viên thành Chủ sở hữu bằng chức năng này.")

        target_member.role = payload.role
        await member_repo.update(target_member)

        return cls._map_member_response(target_member)

    @classmethod
    async def remove_member(
        cls, db: AsyncSession, current_user: User, workspace_id: int, target_user_id: int
    ) -> None:
        """Xóa thành viên khỏi workspace hoặc thành viên tự rời khỏi workspace"""
        member_repo = WorkspaceMemberRepository(db)

        caller_membership = await member_repo.get_member(workspace_id, current_user.id)
        if not caller_membership:
            raise CustomException(403, "Bạn không phải thành viên của không gian làm việc này.")

        target_member = await member_repo.get_member(workspace_id, target_user_id)
        if not target_member:
            raise CustomException(404, "Không tìm thấy thành viên trong workspace.")

        # OWNER không thể bị xóa hoặc tự rời khỏi workspace (phải xóa cả workspace hoặc chuyển nhượng)
        if target_member.role == WorkspaceRole.OWNER:
            raise CustomException(400, "Chủ sở hữu không thể bị xóa hoặc tự rời khỏi workspace.")

        # Trường hợp 1: Tự rời khỏi workspace
        if current_user.id == target_user_id:
            await member_repo.delete(target_member)
            return

        # Trường hợp 2: Người khác xóa
        if caller_membership.role == WorkspaceRole.MEMBER:
            raise CustomException(403, "Thành viên thông thường không có quyền xóa thành viên khác.")

        # ADMIN không thể xóa ADMIN khác hoặc OWNER
        if caller_membership.role == WorkspaceRole.ADMIN and target_member.role in [WorkspaceRole.ADMIN, WorkspaceRole.OWNER]:
            raise CustomException(403, "Quản trị viên không thể xóa Quản trị viên khác hoặc Chủ sở hữu.")

        await member_repo.delete(target_member)
