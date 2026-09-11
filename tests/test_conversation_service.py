"""Prueba de integración de la Fase 1: un turno completo de conversación
(usuario -> Core Orchestrator -> "LLM" -> persistencia) sin depender de
credenciales reales de Claude API. Usa SQLite en memoria (no requiere
Postgres corriendo) y un `LLMClient` falso.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from nexum.core.services.conversation_service import ConversationService
from nexum.db.models import Base, Conversation, User


class FakeLLMClient:
    """Stub de `LLMClient`: no llama a la API real, devuelve una respuesta fija
    y registra con qué mensajes fue invocado.
    """

    def __init__(self, reply: str = "Respuesta de prueba.") -> None:
        self.reply = reply
        self.calls: list[dict] = []

    async def send_message(
        self, *, system: str, messages: list[dict], max_tokens: int = 2048
    ) -> str:
        self.calls.append({"system": system, "messages": messages})
        return self.reply


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s

    await engine.dispose()


async def test_handle_user_message_persists_conversation(session: AsyncSession) -> None:
    fake_llm = FakeLLMClient(reply="¡Hola! Soy Nexum de prueba.")
    service = ConversationService(llm_client=fake_llm)

    reply = await service.handle_user_message(
        session,
        telegram_user_id=123456,
        username="asana",
        first_name="Abimael",
        language_code="es",
        text="Hola, ¿quién eres?",
    )

    assert reply == "¡Hola! Soy Nexum de prueba."

    # Se creó el usuario.
    user = (await session.execute(select(User))).scalar_one()
    assert user.telegram_user_id == 123456
    assert user.username == "asana"

    # Se guardaron ambos lados del turno, en orden.
    messages = (
        (await session.execute(select(Conversation).order_by(Conversation.id))).scalars().all()
    )
    assert [m.direction for m in messages] == ["in", "out"]
    assert messages[0].content == "Hola, ¿quién eres?"
    assert messages[1].content == "¡Hola! Soy Nexum de prueba."

    # El LLM se llamó una vez, con el mensaje del usuario al final.
    assert len(fake_llm.calls) == 1
    assert fake_llm.calls[0]["messages"][-1] == {
        "role": "user",
        "content": "Hola, ¿quién eres?",
    }


async def test_handle_user_message_reuses_history_as_context(session: AsyncSession) -> None:
    fake_llm = FakeLLMClient(reply="ok")
    service = ConversationService(llm_client=fake_llm)

    await service.handle_user_message(
        session,
        telegram_user_id=42,
        username=None,
        first_name="Ana",
        language_code="es",
        text="Me llamo Ana.",
    )
    await service.handle_user_message(
        session,
        telegram_user_id=42,
        username=None,
        first_name="Ana",
        language_code="es",
        text="¿Cómo me llamo?",
    )

    # El segundo turno debe reenviar el historial previo como contexto.
    second_call_messages = fake_llm.calls[1]["messages"]
    assert second_call_messages == [
        {"role": "user", "content": "Me llamo Ana."},
        {"role": "assistant", "content": "ok"},
        {"role": "user", "content": "¿Cómo me llamo?"},
    ]

    # Sigue siendo un único usuario (mismo telegram_user_id).
    users = (await session.execute(select(User))).scalars().all()
    assert len(users) == 1
