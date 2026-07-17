"""Tests del motor de conversación del bot, con un cliente de Anthropic FALSO.

Prueba la máquina de estados y el tool-use sin llamar a la API real: el fake devuelve
respuestas prefabricadas (texto o tool_use). Necesita TEST_DATABASE_URL (usa DB real
porque el motor crea conversaciones, mensajes y leads).
"""

import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.conversation import BotEngine
from app.config import settings
from app.models.bot import BotConversation, BotLead, BotMessage

PHONE = "56911112222"


# --- Cliente Anthropic falso ------------------------------------------------


class FakeBlock:
    def __init__(self, type, text=None, name=None, input=None, id=None):
        self.type = type
        self.text = text
        self.name = name
        self.input = input
        self.id = id


class FakeResponse:
    def __init__(self, stop_reason, content):
        self.stop_reason = stop_reason
        self.content = content


def text_response(text: str) -> FakeResponse:
    return FakeResponse("end_turn", [FakeBlock("text", text=text)])


def tool_response(name: str, tool_input: dict, tool_id: str = "toolu_1") -> FakeResponse:
    return FakeResponse("tool_use", [FakeBlock("tool_use", name=name, input=tool_input, id=tool_id)])


class FakeMessages:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return self._responses.pop(0)


class FakeAnthropic:
    def __init__(self, *responses):
        self.messages = FakeMessages(list(responses))


# --- Fixtures ---------------------------------------------------------------


@pytest_asyncio.fixture
async def db(engine) -> AsyncSession:
    sm = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with sm() as s:
        yield s


async def _count(db, model, **filt) -> int:
    q = select(func.count()).select_from(model)
    for k, v in filt.items():
        q = q.where(getattr(model, k) == v)
    return (await db.execute(q)).scalar_one()


# --- Tests ------------------------------------------------------------------


@pytest.mark.asyncio
class TestConversacion:
    async def test_respuesta_de_texto_simple(self, db):
        fake = FakeAnthropic(text_response("¡Hola! Soy el asistente de Recontrata. ¿En qué te ayudo?"))
        engine = BotEngine(db, fake)

        reply = await engine.handle_message(PHONE, "hola")

        assert "asistente de Recontrata" in reply
        # Se guardó la conversación con el mensaje del usuario y la respuesta.
        assert await _count(db, BotConversation, phone=PHONE) == 1
        assert await _count(db, BotMessage) == 2  # user + assistant

    async def test_config_del_llm_es_la_correcta(self, db):
        """Sonnet 5: thinking disabled, effort low, SIN temperature, system cacheado."""
        fake = FakeAnthropic(text_response("ok"))
        engine = BotEngine(db, fake)
        await engine.handle_message(PHONE, "hola")

        kwargs = fake.messages.calls[0]
        assert kwargs["model"] == settings.BOT_MODEL
        assert kwargs["thinking"] == {"type": "disabled"}
        assert kwargs["output_config"] == {"effort": "low"}
        assert "temperature" not in kwargs and "top_p" not in kwargs
        assert kwargs["system"][0]["cache_control"] == {"type": "ephemeral"}
        assert [t["name"] for t in kwargs["tools"]] == [
            "registrar_prospecto",
            "derivar_a_soporte",
            "escalar_a_humano",
        ]

    async def test_registrar_prospecto_crea_lead_y_avisa(self, db):
        fake = FakeAnthropic(
            tool_response(
                "registrar_prospecto",
                {"name": "Juan Pérez", "company": "Mineralex", "interest": "Cotizar plan Pro"},
            ),
            text_response("Listo Juan, el equipo comercial te contactará pronto."),
        )
        engine = BotEngine(db, fake)

        reply = await engine.handle_message(PHONE, "Quiero contratar, soy Juan de Mineralex")

        assert "contactará" in reply
        assert await _count(db, BotLead) == 1
        lead = (await db.execute(select(BotLead))).scalar_one()
        assert lead.name == "Juan Pérez"
        assert lead.company == "Mineralex"
        assert lead.phone == PHONE
        conv = (await db.execute(select(BotConversation))).scalar_one()
        assert conv.state == "derived"
        assert conv.notified_at is not None

    async def test_no_registra_dos_veces_el_mismo_prospecto(self, db):
        """Guard already_notified: si Claude reintenta registrar, no se duplica el lead."""
        fake = FakeAnthropic(
            tool_response("registrar_prospecto", {"interest": "x"}, tool_id="t1"),
            tool_response("registrar_prospecto", {"interest": "x"}, tool_id="t2"),
            text_response("Ya te tengo registrado."),
        )
        engine = BotEngine(db, fake)
        await engine.handle_message(PHONE, "quiero contratar")
        assert await _count(db, BotLead) == 1

    async def test_derivar_a_soporte_marca_estado(self, db):
        fake = FakeAnthropic(
            tool_response("derivar_a_soporte", {"reason": "No puede entrar a su cuenta"}),
            text_response("Para eso escríbenos a atencion@recontrata.cl y te ayudamos."),
        )
        engine = BotEngine(db, fake)

        reply = await engine.handle_message(PHONE, "soy cliente y no puedo entrar")

        assert "atencion@recontrata.cl" in reply
        assert await _count(db, BotLead) == 0
        conv = (await db.execute(select(BotConversation))).scalar_one()
        assert conv.state == "support"

    async def test_escalar_a_humano_pausa_el_bot(self, db):
        fake = FakeAnthropic(
            tool_response("escalar_a_humano", {"reason": "Pide hablar con un vendedor"}),
            text_response("Un miembro del equipo te va a responder."),
        )
        engine = BotEngine(db, fake)
        reply = await engine.handle_message(PHONE, "quiero hablar con una persona")
        assert "equipo" in reply

        conv = (await db.execute(select(BotConversation))).scalar_one()
        assert conv.handed_off is True

        # Siguiente mensaje: el bot está en pausa, no responde y NO llama al LLM.
        fake2 = FakeAnthropic()  # sin respuestas: si lo llamara, reventaría
        engine2 = BotEngine(db, fake2)
        reply2 = await engine2.handle_message(PHONE, "¿hola?")
        assert reply2 is None
        assert fake2.messages.calls == []

    async def test_misma_conversacion_dentro_de_la_sesion(self, db):
        """Dos mensajes seguidos del mismo teléfono comparten conversación e historial."""
        fake = FakeAnthropic(text_response("respuesta 1"), text_response("respuesta 2"))
        engine = BotEngine(db, fake)
        await engine.handle_message(PHONE, "primera")
        await engine.handle_message(PHONE, "segunda")

        assert await _count(db, BotConversation, phone=PHONE) == 1
        assert await _count(db, BotMessage) == 4  # 2 user + 2 assistant (tras ambas respuestas)
        # La segunda llamada al LLM lleva el historial acumulado hasta ese punto: la
        # primera pregunta, la primera respuesta y la segunda pregunta (3). La segunda
        # respuesta aún no existe cuando se llama al modelo.
        second_call_messages = fake.messages.calls[1]["messages"]
        assert [m["content"] for m in second_call_messages] == ["primera", "respuesta 1", "segunda"]
