"""Avisos por correo del bot (leads y escalamientos), vía Resend HTTP API.

Dos correos:
- `send_lead_email`: cuando el bot capta un prospecto (registrar_prospecto).
- `send_escalation_email`: cuando alguien pide hablar con un humano (escalar_a_humano).

Seguridad de marcha blanca: si `ALERTS_TEST_MODE` está en True (default), TODAS las alertas
se redirigen a `ALERTS_TEST_EMAILS` en vez de a los destinatarios reales — así un despliegue
accidental no le escribe a nadie. Sin `RESEND_API_KEY` (dev/tests), no llama a la red: loguea.
"""

import html

import httpx
import structlog

from app.config import settings

logger = structlog.get_logger()

RESEND_URL = "https://api.resend.com/emails"


def _recipients(default_list: list[str]) -> list[str]:
    """Destinatarios reales, o los de prueba si estamos en marcha blanca."""
    if settings.ALERTS_TEST_MODE:
        return settings.alerts_test_emails_list
    return default_list


async def _send(subject: str, html_body: str, to: list[str]) -> bool:
    if not settings.RESEND_API_KEY or not to:
        logger.info("bot_email_dev_mode", subject=subject, to=to)
        return False
    payload = {
        "from": settings.BOT_FROM_EMAIL,
        "to": to,
        "subject": subject,
        "html": html_body,
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                RESEND_URL, json=payload, headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"}
            )
            r.raise_for_status()
        logger.info("bot_email_sent", subject=subject, to=to)
        return True
    except Exception as e:  # noqa: BLE001
        logger.warning("bot_email_failed", subject=subject, error=str(e))
        return False


def _transcript_html(transcript: list[tuple[str, str]]) -> str:
    rows = []
    for role, content in transcript:
        who = "Cliente" if role == "user" else "Bot"
        rows.append(f"<p style='margin:4px 0'><b>{who}:</b> {html.escape(content)}</p>")
    return "".join(rows) or "<p>(sin mensajes)</p>"


async def send_lead_email(lead: dict, transcript: list[tuple[str, str]]) -> bool:
    """Avisa al equipo comercial de un prospecto nuevo. `lead` es un snapshot de datos."""
    title_parts = [p for p in (lead.get("name"), lead.get("company")) if p]
    subject = "[LEAD Recontrata] " + (" — ".join(title_parts) if title_parts else lead.get("phone", ""))
    fields = "".join(
        f"<li><b>{label}:</b> {html.escape(str(value))}</li>"
        for label, value in [
            ("Nombre", lead.get("name")),
            ("Empresa", lead.get("company")),
            ("Correo", lead.get("email")),
            ("Teléfono (WhatsApp)", lead.get("phone")),
            ("Rubro", lead.get("industry")),
            ("Trabajadores (aprox.)", lead.get("workers_estimate")),
            ("Interés", lead.get("interest")),
        ]
        if value
    )
    body = (
        "<h2>Nuevo prospecto desde el bot de WhatsApp</h2>"
        f"<ul>{fields}</ul>"
        "<hr><h3>Conversación</h3>"
        f"{_transcript_html(transcript)}"
    )
    return await _send(subject, body, _recipients(settings.bot_lead_emails_list))


async def send_escalation_email(phone: str, reason: str, transcript: list[tuple[str, str]]) -> bool:
    """Avisa que un prospecto pide atención humana (el bot quedó en pausa)."""
    subject = f"[ESCALAMIENTO Recontrata] {phone} pide atención humana"
    body = (
        "<h2>Un prospecto pide hablar con una persona</h2>"
        f"<p><b>Teléfono (WhatsApp):</b> {html.escape(phone)}</p>"
        f"<p><b>Motivo:</b> {html.escape(reason or '—')}</p>"
        "<p>El bot quedó en pausa en esta conversación; respóndele tú por WhatsApp.</p>"
        "<hr><h3>Conversación</h3>"
        f"{_transcript_html(transcript)}"
    )
    return await _send(subject, body, _recipients(settings.bot_lead_emails_list))
