"""Comandos de sistema: `/start` y `/ping`.

La conversación libre (delegada al Core Orchestrator / Claude API) se
maneja en `nexum.bot.handlers.chat`.
"""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router(name="system")


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "👋 ¡Hola! Soy Nexum, tu asistente personal.\n"
        "Todavía estoy en construcción (sin roles ni recordatorios aún), "
        "pero ya puedes hablarme libremente."
    )


@router.message(Command("ping"))
async def handle_ping(message: Message) -> None:
    await message.answer("pong 🏓")
