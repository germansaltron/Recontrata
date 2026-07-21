"""Tests del buffer de mensajes del bot (M4): agrupar una ráfaga fragmentada de
WhatsApp en una sola respuesta, en vez de contestar cada línea por separado.

Sin DB: se mockea _process_bot_message para capturar qué se procesa y cuándo.
"""
import asyncio

import pytest

from app.api.v1 import whatsapp
from app.config import settings


@pytest.fixture
def fast_buffer(monkeypatch):
    # Ventana corta para que el test sea rápido, y estado global limpio.
    monkeypatch.setattr(settings, "MESSAGE_BUFFER_SECONDS", 0.05)
    whatsapp._msg_buffers.clear()
    whatsapp._msg_timers.clear()


async def test_agrupa_mensajes_de_una_rafaga(monkeypatch, fast_buffer):
    calls: list[tuple[str, str]] = []

    async def fake_process(phone: str, text: str):
        calls.append((phone, text))

    monkeypatch.setattr(whatsapp, "_process_bot_message", fake_process)

    # Tres líneas seguidas, dentro de la ventana: deben procesarse como UNA.
    whatsapp.buffer_message("569111", "Hola")
    whatsapp.buffer_message("569111", "quiero info")
    whatsapp.buffer_message("569111", "de los planes")
    await asyncio.sleep(0.15)

    assert calls == [("569111", "Hola\nquiero info\nde los planes")]


async def test_mensajes_separados_en_el_tiempo_no_se_agrupan(monkeypatch, fast_buffer):
    calls: list[tuple[str, str]] = []

    async def fake_process(phone: str, text: str):
        calls.append((phone, text))

    monkeypatch.setattr(whatsapp, "_process_bot_message", fake_process)

    whatsapp.buffer_message("569222", "primero")
    await asyncio.sleep(0.15)  # pasa la ventana → se procesa
    whatsapp.buffer_message("569222", "segundo")
    await asyncio.sleep(0.15)

    assert calls == [("569222", "primero"), ("569222", "segundo")]


async def test_telefonos_distintos_no_se_mezclan(monkeypatch, fast_buffer):
    calls: list[tuple[str, str]] = []

    async def fake_process(phone: str, text: str):
        calls.append((phone, text))

    monkeypatch.setattr(whatsapp, "_process_bot_message", fake_process)

    whatsapp.buffer_message("569333", "soy A")
    whatsapp.buffer_message("569444", "soy B")
    await asyncio.sleep(0.15)

    assert sorted(calls) == [("569333", "soy A"), ("569444", "soy B")]
