"""Wrapper async sobre el SDK oficial `anthropic` para el Core Orchestrator.

Fase 1: una única llamada a `messages.create` (mensaje -> respuesta), sin
tools todavía. El loop de tool use (function calling: recordatorios, cambio
de rol, memoria) se añade en Fase 3 sobre esta misma clase.
"""

from __future__ import annotations

import logging

import anthropic

from nexum.config import settings

logger = logging.getLogger(__name__)

# Límite conservador: los mensajes de Telegram no superan ~4096 caracteres,
# así que no hay razón para pedirle al modelo una respuesta mucho más larga.
DEFAULT_MAX_TOKENS = 2048


class LLMError(Exception):
    """Error de cara al usuario al fallar una llamada a Claude API.

    El Core la captura para responder algo razonable en Telegram sin
    filtrar detalles internos (stack traces, status codes) al usuario.
    """


class LLMClient:
    """Cliente de alto nivel para conversar con Claude."""

    def __init__(self, *, api_key: str | None = None, model: str | None = None) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key or settings.anthropic_api_key)
        self._model = model or settings.anthropic_model

    async def send_message(
        self,
        *,
        system: str,
        messages: list[dict],
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> str:
        """Envía el historial de conversación y devuelve el texto de respuesta.

        `system` se marca como cacheable (`cache_control: ephemeral`): es
        contenido estable por rol que se reutiliza en cada turno del mismo
        usuario (ver docs/ARCHITECTURE.md §6.3).
        """
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
                messages=messages,
            )
        except anthropic.RateLimitError as e:
            retry_after = e.response.headers.get("retry-after", "unos segundos")
            logger.warning("Rate limited por Claude API, retry-after=%s", retry_after)
            raise LLMError(
                "Estoy recibiendo muchos mensajes ahora mismo, intenta de nuevo en un momento."
            ) from e
        except anthropic.AuthenticationError as e:
            logger.error("ANTHROPIC_API_KEY inválida o ausente.")
            raise LLMError("El asistente no está configurado correctamente.") from e
        except anthropic.PermissionDeniedError as e:
            logger.error("La API key no tiene permisos suficientes para el modelo %s.", self._model)
            raise LLMError("El asistente no tiene permisos para responder ahora mismo.") from e
        except anthropic.NotFoundError as e:
            logger.error("Modelo o endpoint inválido: %s", self._model)
            raise LLMError("Configuración del modelo inválida.") from e
        except anthropic.BadRequestError as e:
            logger.error("Bad request a Claude API: %s", e.message)
            raise LLMError("No pude procesar ese mensaje.") from e
        except anthropic.APIStatusError as e:
            if e.status_code >= 500:
                logger.error("Error de servidor en Claude API (%s): %s", e.status_code, e.message)
                raise LLMError(
                    "El servicio de IA no está disponible ahora mismo, intenta más tarde."
                ) from e
            logger.error("Error de la API de Claude (%s): %s", e.status_code, e.message)
            raise LLMError("No pude procesar ese mensaje.") from e
        except anthropic.APIConnectionError as e:
            logger.error("Error de conexión con Claude API: %s", e)
            raise LLMError("No pude conectar con el asistente, intenta de nuevo.") from e
        except Exception as e:
            # Red de seguridad: errores que el SDK lanza antes de llegar a
            # hacer la request (p. ej. TypeError si no hay ninguna
            # credencial resuelta) no son subclases de `anthropic.*` y no
            # los captura ninguno de los except anteriores.
            logger.exception("Error inesperado llamando a Claude API: %s", e)
            raise LLMError("El asistente no está configurado correctamente.") from e

        if response.stop_reason == "refusal":
            category = getattr(response.stop_details, "category", None)
            logger.info("Claude rechazó la solicitud (categoría=%s).", category)
            return "No puedo ayudarte con eso."

        text = next((block.text for block in response.content if block.type == "text"), "")
        return text or "No tengo una respuesta para eso ahora mismo."
