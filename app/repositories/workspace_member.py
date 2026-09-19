from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models.workspace import WorkspaceMember
from app.repositories.base import BaseRepository


class WorkspaceMemberRepository(BaseRepository[WorkspaceMember]):
    def __init__(self, db: AsyncSession):
        super().__init__(WorkspaceMember, db)

    async def get_member(self, workspace_id: int, user_id: int) -> Optional[WorkspaceMember]:
        """Lấy thông tin thành viên theo workspace_id và user_id"""
        stmt = (
            select(WorkspaceMember)
            .where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
            .options(joinedload(WorkspaceMember.user))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_members_by_workspace(self, workspace_id: int) -> List[WorkspaceMember]:
        """Lấy danh sách thành viên của workspace kèm thông tin User"""
        stmt = (
            select(WorkspaceMember)
            .where(WorkspaceMember.workspace_id == workspace_id)
            .options(joinedload(WorkspaceMember.user))
            .order_by(WorkspaceMember.joined_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
