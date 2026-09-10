"""Repositorio de usuarios."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexum.db.models import User


async def get_or_create_user(
    session: AsyncSession,
    *,
    telegram_user_id: int,
    username: str | None = None,
    first_name: str | None = None,
    language_code: str | None = None,
) -> User:
    """Busca al usuario por su `telegram_user_id`; lo crea si no existe.

    Si el usuario ya existe, actualiza `username`/`first_name` por si
    cambiaron en Telegram (no se pisa el resto de la configuración).
    """
    result = await session.execute(select(User).where(User.telegram_user_id == telegram_user_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_user_id=telegram_user_id,
            username=username,
            first_name=first_name,
            language_code=language_code,
        )
        session.add(user)
        await session.flush()
        return user

    user.username = username
    user.first_name = first_name
    return user
