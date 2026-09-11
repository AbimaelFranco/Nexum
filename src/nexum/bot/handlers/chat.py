"""Handler de conversación libre: delega en el Core Orchestrator (Claude API).

Cualquier mensaje de texto que no matchee un comando de `system.py` llega
aquí. Este router debe registrarse *después* del de comandos (ver
`nexum.bot.__main__`), ya que no tiene filtro y capturaría todo primero.
"""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.types import Message

from nexum.core.llm.client import LLMError
from nexum.core.services.conversation_service import ConversationService
from nexum.db.session import async_session_factory

logger = logging.getLogger(__name__)

router = Router(name="chat")

_conversation_service = ConversationService()


@router.message()
async def handle_chat_message(message: Message) -> None:
    if not message.text:
        await message.answer("Por ahora solo entiendo texto 🙂")
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    async with async_session_factory() as session:
        try:
            reply = await _conversation_service.handle_user_message(
                session,
                telegram_user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                language_code=message.from_user.language_code,
                text=message.text,
            )
        except LLMError as e:
            await session.rollback()
            logger.warning("LLMError al responder a %s: %s", message.from_user.id, e)
            await message.answer(str(e))
            return
        except Exception:
            await session.rollback()
            logger.exception("Error inesperado al procesar mensaje de %s", message.from_user.id)
            await message.answer("Algo salió mal de mi lado, intenta de nuevo en un momento.")
            return

    await message.answer(reply)
