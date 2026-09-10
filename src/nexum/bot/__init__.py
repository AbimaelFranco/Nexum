"""Bot Gateway: capa de integración con la API de Telegram (aiogram).

Responsable de comandos, menús inline y máquinas de estado (FSM) de
conversación. La lógica de negocio (roles, LLM, recordatorios) vive en
`nexum.core` y `nexum.scheduler`; este módulo no debe contenerla.
"""
