# Imagen única para todos los servicios de Nexum (app/bot y scheduler).
# El proceso a ejecutar se decide por `command:` en docker-compose, no aquí,
# para mantener una sola imagen mientras el proyecto es un modular monolito.

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias del sistema mínimas (se amplía en fases futuras si asyncpg u
# otras libs las requieren en build).
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md alembic.ini ./
COPY src ./src
COPY alembic ./alembic

# Instalación editable: el paquete importado apunta a /app/src en vez de a
# una copia en site-packages, para que el bind mount `./src:/app/src:ro` de
# docker-compose.yml (desarrollo) sirva código actualizado sin rebuild.
RUN pip install -e .

# Usuario sin privilegios
RUN useradd --create-home --uid 1000 nexum
USER nexum

# Entrypoint por defecto: bot en modo polling.
# El servicio `scheduler` en docker-compose lo sobreescribe con:
#   command: ["python", "-m", "nexum.scheduler"]
CMD ["python", "-m", "nexum.bot"]
