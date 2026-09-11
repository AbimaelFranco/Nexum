# Nexum

Nexum is a configurable, proactive AI assistant for Telegram. It connects users with an AI model through a customizable prompt, enabling conversational assistance, personalized guidance, automated follow-ups, and scheduled interactions for virtually any use case.

La planeación completa de la arquitectura está en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
El checklist de tareas vive en [GitHub Issues](https://github.com/AbimaelFranco/Nexum/issues) (8 milestones, una por fase) y en el [Project board](https://github.com/users/AbimaelFranco/projects/7).

## Estado actual

🚧 **Fase 1 — MVP conversacional.** El bot conversa usando Claude API (sin roles todavía: un único prompt genérico) y persiste el historial en Postgres. `/ping` sigue disponible como comando de salud.

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

Edita `.env` y completa:
- `TELEGRAM_BOT_TOKEN` — el token del paso anterior.
- `ANTHROPIC_API_KEY` — tu clave de la [consola de Anthropic](https://console.anthropic.com/) (API Keys). Sin esto el bot arranca igual, pero responde con un mensaje de error en vez de conversar.

`.env` nunca se sube al repositorio (ya está en `.gitignore`).

## 3. Levantar el entorno con Docker

```bash
docker compose up --build
```

Esto levanta `app` (el bot, en modo polling), `postgres` y `redis`.

## 4. Aplicar las migraciones de base de datos

Con el stack arriba, en otra terminal:

```bash
docker compose exec app python -m alembic upgrade head
```

(Solo hace falta una vez, y de nuevo cada vez que se agregue una migración nueva.)

Al terminar, escribe `/start` o cualquier mensaje a tu bot en Telegram — debería responder usando Claude.

### Desarrollo: cambios en `src/` sin rebuild

El servicio `app` monta `./src` dentro del contenedor y el paquete se instala en modo editable (`pip install -e .`), así que editar código en `src/` y reiniciar el contenedor (`docker compose restart app`) es suficiente — no hace falta `docker compose build` salvo que cambien las dependencias en `pyproject.toml`.

## Desarrollo local sin Docker (opcional)

Requiere Postgres y Redis accesibles (por ejemplo, levantados con `docker compose up -d postgres redis` y `POSTGRES_HOST=localhost` en tu `.env`).

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
python -m alembic upgrade head
python -m nexum.bot
```

> **Nota (Windows + Docker Desktop):** conectar `asyncpg` desde el host a un Postgres en contenedor puede fallar con `ConnectionResetError` por cómo Docker Desktop reenvía el puerto en Windows. Si te pasa, corre Alembic dentro del contenedor en vez de en el host: `docker compose exec app python -m alembic upgrade head`.

## Estructura del proyecto

Ver [docs/ARCHITECTURE.md §11](docs/ARCHITECTURE.md#11-estructura-de-carpetas-propuesta).
