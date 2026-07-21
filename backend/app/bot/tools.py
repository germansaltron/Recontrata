"""Herramientas (tool-use) que Claude puede invocar en la conversación.

Ninguna toca datos del producto (trabajadores, evaluaciones): el bot es solo de ventas.
Las descripciones son PRESCRIPTIVAS ("Llama a esto cuando...") a propósito: Sonnet con
thinking apagado invoca menos herramientas, así que hay que decirle claramente el gatillo.

La ejecución vive en conversation.py; acá solo están las definiciones (esquemas).
"""

from app.config import settings

TOOLS = [
    {
        "name": "registrar_prospecto",
        "description": (
            "Registra a un prospecto interesado y avisa al equipo comercial. "
            "LLAMA A ESTO cuando la persona muestra interés comercial real (quiere contratar, "
            "pedir una demo, saber cómo empezar, o que lo contacten) Y ya tienes al menos su "
            "nombre y su empresa. El teléfono ya lo tenemos por WhatsApp; el correo es un plus. "
            "No lo llames por una duda suelta sin intención; primero conversa y resuelve. "
            "Después de registrarlo, confirma a la persona que el equipo la contactará."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nombre de la persona."},
                "company": {"type": "string", "description": "Empresa o contratista al que pertenece."},
                "email": {"type": "string", "description": "Correo electrónico, si lo entrega."},
                "industry": {
                    "type": "string",
                    "description": "Rubro: mineria, construccion, energia, logistica u otro.",
                },
                "workers_estimate": {
                    "type": "string",
                    "description": "Cuántos trabajadores maneja, aprox. Banda: '1-15', '16-100', '100-500' o '500+'.",
                },
                "interest": {
                    "type": "string",
                    "description": "En una frase, qué necesita o qué le interesó (para el equipo comercial).",
                },
            },
            "required": ["interest"],
        },
    },
    {
        "name": "derivar_a_soporte",
        "description": (
            f"Deriva a la persona al correo de soporte ({settings.BOT_SUPPORT_EMAIL}). "
            "LLAMA A ESTO cuando quien escribe es un CLIENTE que YA usa Recontrata y necesita "
            "ayuda con su cuenta (no puede entrar, un problema técnico, cómo hacer algo dentro "
            "de la plataforma, facturación). El bot es de ventas, no de soporte: no intentes "
            "resolver el problema técnico, entrega el correo y cierra con amabilidad."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "En una frase, qué necesita el cliente (para el registro).",
                }
            },
            "required": [],
        },
    },
    {
        "name": "escalar_a_humano",
        "description": (
            "Avisa a una persona del equipo y PAUSA el bot en esta conversación. "
            "LLAMA A ESTO cuando la persona pide explícitamente hablar con un humano/vendedor, "
            "o cuando la conversación se traba y claramente necesita atención personal que tú no "
            "puedes dar. Tras llamarlo, dile que un miembro del equipo le va a responder."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "En una frase, por qué se escala (para avisar al equipo).",
                }
            },
            "required": [],
        },
    },
]
