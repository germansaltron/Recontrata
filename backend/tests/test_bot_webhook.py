"""Tests unitarios del webhook de WhatsApp: firma HMAC y parseo del sobre de Meta.

Sin DB — corren siempre. Los de recepción punta a punta están en
tests/integration/test_bot_webhook.py.
"""

import hashlib
import hmac

from app.api.v1.whatsapp import extract_messages, is_blocked, message_text, verify_signature
from app.config import settings

APP_SECRET = "test_app_secret_para_firmar"


def sign(body: bytes, secret: str = APP_SECRET) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def wa_payload(wamid: str = "wamid.TEST1", phone: str = "56912345678", text: str = "Hola") -> dict:
    """Sobre de Meta, con la anidación real: entry → changes → value → messages."""
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_ID",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"phone_number_id": "PHONE_ID"},
                            "messages": [
                                {
                                    "from": phone,
                                    "id": wamid,
                                    "timestamp": "1750000000",
                                    "type": "text",
                                    "text": {"body": text},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


class TestVerifySignature:
    def test_firma_valida(self, monkeypatch):
        monkeypatch.setattr(settings, "META_APP_SECRET", APP_SECRET)
        body = b'{"hola":"mundo"}'
        assert verify_signature(body, sign(body)) is True

    def test_firma_de_otro_secreto_se_rechaza(self, monkeypatch):
        monkeypatch.setattr(settings, "META_APP_SECRET", APP_SECRET)
        body = b'{"hola":"mundo"}'
        assert verify_signature(body, sign(body, "secreto_del_atacante")) is False

    def test_cuerpo_alterado_invalida_la_firma(self, monkeypatch):
        monkeypatch.setattr(settings, "META_APP_SECRET", APP_SECRET)
        firma = sign(b'{"monto":100}')
        assert verify_signature(b'{"monto":999}', firma) is False

    def test_sin_header_se_rechaza(self, monkeypatch):
        monkeypatch.setattr(settings, "META_APP_SECRET", APP_SECRET)
        assert verify_signature(b"{}", None) is False

    def test_header_sin_prefijo_sha256_se_rechaza(self, monkeypatch):
        monkeypatch.setattr(settings, "META_APP_SECRET", APP_SECRET)
        body = b"{}"
        crudo = hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
        assert verify_signature(body, crudo) is False

    def test_sin_app_secret_configurado_falla_cerrado(self, monkeypatch):
        """Sin credencial no se valida nada: ni siquiera una firma bien construida pasa."""
        monkeypatch.setattr(settings, "META_APP_SECRET", "")
        body = b"{}"
        assert verify_signature(body, sign(body)) is False


class TestExtraccion:
    def test_extrae_mensaje_de_texto(self):
        msgs = extract_messages(wa_payload())
        assert len(msgs) == 1
        assert message_text(msgs[0]) == "Hola"

    def test_ignora_eventos_de_estado(self):
        """Meta manda `statuses` (entregado/leído) por el mismo webhook: no son mensajes."""
        payload = {"entry": [{"changes": [{"value": {"statuses": [{"id": "wamid.X", "status": "delivered"}]}}]}]}
        assert extract_messages(payload) == []

    def test_payload_vacio_no_revienta(self):
        assert extract_messages({}) == []
        assert extract_messages({"entry": [{"changes": [{"value": {}}]}]}) == []

    def test_media_sin_caption_se_degrada_a_marcador(self):
        msg = {"type": "image", "image": {"id": "MEDIA1", "mime_type": "image/jpeg"}}
        assert message_text(msg) == "[image]"

    def test_media_con_caption_usa_el_caption(self):
        msg = {"type": "image", "image": {"id": "MEDIA1", "caption": "esta es mi faena"}}
        assert message_text(msg) == "esta es mi faena"

    def test_boton_interactivo_usa_el_titulo(self):
        msg = {"type": "interactive", "interactive": {"button_reply": {"id": "b1", "title": "Ver planes"}}}
        assert message_text(msg) == "Ver planes"


class TestBloqueo:
    def test_bloquea_sin_importar_el_formato(self, monkeypatch):
        monkeypatch.setattr(settings, "BLOCKED_NUMBERS", '["+56 9 1234 5678"]')
        assert is_blocked("56912345678") is True

    def test_numero_no_bloqueado_pasa(self, monkeypatch):
        monkeypatch.setattr(settings, "BLOCKED_NUMBERS", '["56900000000"]')
        assert is_blocked("56912345678") is False

    def test_sin_lista_de_bloqueo_pasa(self, monkeypatch):
        monkeypatch.setattr(settings, "BLOCKED_NUMBERS", "[]")
        assert is_blocked("56912345678") is False
