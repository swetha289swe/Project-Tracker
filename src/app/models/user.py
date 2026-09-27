import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    memberships: Mapped[list["ProjectMember"]] = relationship(back_populates="user")  # noqa: F821
    role: Mapped[str | None] = mapped_column(String(500), nullable=False,default="MEMBER",server_default="MEMBER")

    @validates("role")
    def normalize_role(self, key, value):
        if value is None:
            return "MEMBER"
        return value.upper()
# class RefreshToken(Base):
#     __tablename__ = "refresh_tokens"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
#     )
#     user_id: Mapped[uuid.UUID] = mapped_column(
#         ForeignKey("users.id", ondelete="CASCADE"), index=True
#     )
#     token_hash: Mapped[str] = mapped_column(String(128), unique=True)
#     expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
#     revoked: Mapped[bool] = mapped_column(Boolean, default=False)