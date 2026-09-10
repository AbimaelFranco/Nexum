# Nexum

Nexum is a configurable, proactive AI assistant for Telegram. It connects users with an AI model through a customizable prompt, enabling conversational assistance, personalized guidance, automated follow-ups, and scheduled interactions for virtually any use case.

La planeación completa de la arquitectura está en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
El checklist de tareas vive en [GitHub Issues](https://github.com/AbimaelFranco/Nexum/issues) (8 milestones, una por fase) y en el [Project board](https://github.com/users/AbimaelFranco/projects/7).

## Estado actual

🚧 **Fase 0 — Fundamentos.** El bot solo responde en modo "eco" (`/start`, `/ping`, y repite cualquier texto). Todavía no hay integración con Claude API ni roles.

## Requisitos

- [Docker](https://www.docker.com/) y Docker Compose
- Un bot de Telegram registrado en **@BotFather**

## 1. Registrar el bot en Telegram (BotFather)

Este paso es manual — no existe una API pública para crearlo por script:

1. Abre Telegram y busca **@BotFather**.
2. Envía `/newbot` y sigue las instrucciones (nombre visible y `username` que debe terminar en `bot`, ej. `nexum_asana_bot`).
3. BotFather te entregará un **token** con el formato `123456789:ABC-...`. Guárdalo, lo necesitas en el paso 2.
4. (Opcional, recomendado) Envía `/setprivacy` a BotFather y desactívalo (`Disable`) si quieres que el bot vea todos los mensajes del chat, o déjalo activado si solo debe reaccionar a comandos/menciones en grupos. En chats 1:1 no afecta.

## 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y completa como mínimo:
- `TELEGRAM_BOT_TOKEN` — el token del paso anterior.
- `ANTHROPIC_API_KEY` — tu clave de la API de Claude (no se usa todavía en Fase 0, pero ya se puede dejar configurada).

`.env` nunca se sube al repositorio (ya está en `.gitignore`).

## 3. Levantar el entorno con Docker

```bash
docker compose up --build
```

Esto levanta `app` (el bot, en modo polling), `postgres` y `redis`. Al terminar de iniciar, escribe `/start` o cualquier mensaje a tu bot en Telegram — debería responder.

## Desarrollo local sin Docker (opcional)

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
python -m nexum.bot
```

## Estructura del proyecto

Ver [docs/ARCHITECTURE.md §11](docs/ARCHITECTURE.md#11-estructura-de-carpetas-propuesta).
