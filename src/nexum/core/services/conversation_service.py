"""Orquesta un turno completo de conversación.

Fase 1: carga el historial reciente del usuario, llama al LLM con el
system prompt genérico y persiste ambos lados del turno. A partir de
Fase 2 esto se extiende para construir el prompt según el rol activo, y en
Fase 3 para ejecutar tools (function calling).
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from nexum.core.llm.client import LLMClient
from nexum.core.llm.roles.default import DEFAULT_SYSTEM_PROMPT
from nexum.db.repositories.conversations import add_message, get_recent_messages
from nexum.db.repositories.users import get_or_create_user

# Cuántos turnos previos se reenvían como contexto en cada llamada. Se
# reemplaza en Fase 6 por una estrategia de compactación cuando la
# conversación crece más allá de esta ventana.
HISTORY_LIMIT = 20


class ConversationService:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm = llm_client or LLMClient()

    async def handle_user_message(
        self,
        session: AsyncSession,
        *,
        telegram_user_id: int,
        username: str | None,
        first_name: str | None,
        language_code: str | None,
        text: str,
    ) -> str:
        """Procesa un mensaje entrante y devuelve el texto de respuesta.

        Puede propagar `nexum.core.llm.client.LLMError`; el llamador decide
        cómo comunicárselo al usuario.
        """
        user = await get_or_create_user(
            session,
            telegram_user_id=telegram_user_id,
            username=username,
            first_name=first_name,
            language_code=language_code,
        )

        history = await get_recent_messages(session, user_id=user.id, limit=HISTORY_LIMIT)
        messages = [
            {"role": "user" if m.direction == "in" else "assistant", "content": m.content}
            for m in history
        ]
        messages.append({"role": "user", "content": text})

        reply = await self._llm.send_message(system=DEFAULT_SYSTEM_PROMPT, messages=messages)

        await add_message(session, user_id=user.id, direction="in", content=text)
        await add_message(session, user_id=user.id, direction="out", content=reply)
        await session.commit()

        return reply
