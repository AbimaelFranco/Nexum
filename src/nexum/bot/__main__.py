"""Entrypoint del Bot Gateway: `python -m nexum.bot`.

Fase 0: long polling únicamente (no requiere HTTPS ni dominio público).
El modo webhook se añade en Fase 7 para producción.
"""

from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from nexum.bot.handlers.chat import router as chat_router
from nexum.bot.handlers.system import router as system_router
from nexum.config import settings


async def main() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    log = logging.getLogger("nexum.bot")

    if not settings.telegram_bot_token:
        log.error(
            "TELEGRAM_BOT_TOKEN no está configurado. "
            "Copia .env.example a .env y completa el token de @BotFather."
        )
        sys.exit(1)

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()
    # Orden importa: `chat_router` no tiene filtro y capturaría todo si
    # se registrara antes que los comandos específicos de `system_router`.
    dispatcher.include_router(system_router)
    dispatcher.include_router(chat_router)

    log.info("Nexum bot iniciando en modo polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
