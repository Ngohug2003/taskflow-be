from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

    async def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def revoke_token(self, token_hash: str) -> bool:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(revoked_at=datetime.now(timezone.utc))
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def revoke_all_user_tokens(self, user_id: UUID) -> int:
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None)
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
