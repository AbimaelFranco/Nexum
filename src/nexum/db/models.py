"""Modelos SQLAlchemy de Nexum.

Fase 1: `User` y `Conversation` (historial de mensajes). El resto del
esquema de docs/ARCHITECTURE.md §5 (`roles`, `user_configs`, `events`,
`reminders`, `tool_call_audit`) se añade en las fases correspondientes.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(Text)
    first_name: Mapped[str | None] = mapped_column(Text)
    language_code: Mapped[str | None] = mapped_column(Text)
    timezone: Mapped[str] = mapped_column(Text, default="UTC", server_default="UTC")
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    conversations: Mapped[list[Conversation]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - solo para debugging
        return f"User(id={self.id}, telegram_user_id={self.telegram_user_id})"


class Conversation(Base):
    """Un turno de la conversación (un mensaje entrante o saliente).

    `role_key` identifica el rol activo del usuario en el momento del turno
    (en Fase 1 siempre "default"; a partir de Fase 2 refleja el catálogo de
    roles). No confundir con `direction`, que indica el sentido del mensaje.
    """

    __tablename__ = "conversations"
    __table_args__ = (CheckConstraint("direction IN ('in', 'out')", name="ck_direction"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role_key: Mapped[str] = mapped_column(Text, default="default", server_default="default")
    direction: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    user: Mapped[User] = relationship(back_populates="conversations")

    def __repr__(self) -> str:  # pragma: no cover - solo para debugging
        return f"Conversation(id={self.id}, user_id={self.user_id}, direction={self.direction!r})"
