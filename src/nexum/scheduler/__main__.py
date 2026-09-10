"""Entrypoint del Scheduler Service: `python -m nexum.scheduler`.

Fase 0: stub que solo valida que el entrypoint del contenedor funciona.
La lógica real (APScheduler + jobstore persistente) se implementa en Fase 3.
"""

from __future__ import annotations

import logging

from nexum.config import settings


def main() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logging.getLogger("nexum.scheduler").info(
        "Scheduler stub (Fase 0): sin jobs todavía. Implementación real en Fase 3."
    )


if __name__ == "__main__":
    main()
