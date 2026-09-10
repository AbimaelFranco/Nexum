"""Handler mínimo de validación (Fase 0): responde con un eco a cualquier texto.

Se reemplaza en Fase 1 por el flujo real (mensaje -> Core Orchestrator -> Claude
API -> respuesta), una vez exista la integración con el LLM.
"""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router(name="echo")


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "👋 ¡Hola! Soy Nexum, todavía en construcción.\n"
        "Por ahora solo repito lo que me escribas (modo eco de Fase 0)."
    )


@router.message(Command("ping"))
async def handle_ping(message: Message) -> None:
    await message.answer("pong 🏓")


@router.message()
async def handle_echo(message: Message) -> None:
    text = message.text or "(mensaje sin texto)"
    await message.answer(f"Eco: {text}")
