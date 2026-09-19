from datetime import datetime, timezone
import enum
from typing import Optional
import sqlalchemy as sa
from sqlalchemy import String, Text, ForeignKey, BigInteger, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseDbModel


class WorkspaceRole(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class Workspace(BaseDbModel):
    __tablename__ = "workspaces"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    owner = relationship("User", foreign_keys=[owner_id], lazy="joined")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceMember(BaseDbModel):
    __tablename__ = "workspace_members"
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role: Mapped[WorkspaceRole] = mapped_column(
        Enum(WorkspaceRole, native_enum=False, length=20),
        default=WorkspaceRole.MEMBER,
        nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        default=lambda: datetime.now(timezone.utc)
    )

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", foreign_keys=[user_id], lazy="joined")
