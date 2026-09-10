"""Repositorio de historial de conversación."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexum.db.models import Conversation

DEFAULT_ROLE_KEY = "default"


async def add_message(
    session: AsyncSession,
    *,
    user_id: int,
    direction: str,
    content: str,
    role_key: str = DEFAULT_ROLE_KEY,
) -> Conversation:
    if direction not in ("in", "out"):
        raise ValueError(f"direction inválido: {direction!r} (debe ser 'in' u 'out')")

    message = Conversation(user_id=user_id, direction=direction, content=content, role_key=role_key)
    session.add(message)
    await session.flush()
    return message


async def get_recent_messages(
    session: AsyncSession, *, user_id: int, limit: int = 20
) -> list[Conversation]:
    """Devuelve los últimos `limit` turnos del usuario, en orden cronológico.

    Ordena por `id` (no por `created_at`): dos turnos consecutivos del mismo
    request pueden compartir marca de tiempo según la resolución del reloj
    de la base de datos, y `id` sí garantiza el orden real de inserción.
    """
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.id.desc())
        .limit(limit)
    )
    messages = list(result.scalars().all())
    messages.reverse()
    return messages
