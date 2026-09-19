from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from app.models.workspace import Workspace, WorkspaceMember
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self, db: AsyncSession):
        super().__init__(Workspace, db)

    async def get_workspaces_for_user(self, user_id: int) -> List[Tuple[Workspace, WorkspaceMember]]:
        """Lấy danh sách workspace mà user tham gia kèm bản ghi membership của user"""
        stmt = (
            select(Workspace, WorkspaceMember)
            .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
            .where(WorkspaceMember.user_id == user_id)
            .order_by(Workspace.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.all())

    async def get_with_members(self, workspace_id: int) -> Optional[Workspace]:
        """Lấy chi tiết workspace kèm danh sách members và thông tin User"""
        stmt = (
            select(Workspace)
            .where(Workspace.id == workspace_id)
            .options(
                selectinload(Workspace.members).joinedload(WorkspaceMember.user),
                joinedload(Workspace.owner),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def count_members(self, workspace_id: int) -> int:
        stmt = select(func.count()).select_from(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id)
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0
