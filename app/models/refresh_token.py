from datetime import datetime
from typing import Optional
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy import String, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseDbModel


class RefreshToken(BaseDbModel):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True
    )

    user = relationship("User", backref="refresh_tokens", lazy="joined")
