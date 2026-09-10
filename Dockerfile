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

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install .

# Usuario sin privilegios
RUN useradd --create-home --uid 1000 nexum
USER nexum

# Entrypoint por defecto: bot en modo polling.
# El servicio `scheduler` en docker-compose lo sobreescribe con:
#   command: ["python", "-m", "nexum.scheduler"]
CMD ["python", "-m", "nexum.bot"]
