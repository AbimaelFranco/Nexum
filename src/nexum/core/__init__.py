"""Core Orchestrator: construcción de prompts por rol, integración con Claude
API (function calling) y ejecución de las acciones que el modelo decide
invocar (recordatorios, cambios de configuración, memoria).

Fase 1: conversación básica sin roles ni tools (`llm.client`,
`services.conversation_service`). Roles a partir de Fase 2, tools a partir
de Fase 3.
"""
