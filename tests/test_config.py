"""Prueba de humo: la configuración se importa y expone valores por defecto."""

from nexum.config import Settings


def test_settings_defaults() -> None:
    s = Settings(_env_file=None)
    assert s.postgres_db == "nexum"
    assert s.anthropic_model == "claude-opus-5"
    assert s.database_url.startswith("postgresql+asyncpg://")
