"""Base de conocimiento comercial del bot de ventas.

La parte de PLANES Y PRECIOS se genera desde `app.billing.plans` (la fuente de verdad
del producto), así nunca se desincroniza: si cambian los precios en el código, el bot
los dice bien sin tocar este archivo. El resto —qué es, el problema, cómo funciona— es
la propuesta de valor destilada de JUSTIFICACION_FAENASCORE.md.

Este texto va dentro del prompt de sistema (que se cachea), así que es ESTABLE por
release. No meter aquí nada que cambie por conversación.
"""

from app.billing.plans import (
    PLAN_DISPLAY_NAME,
    PLAN_LIMITS,
    PLAN_PRICES_CLP,
    TRIAL_PERIOD_DAYS,
    BillingPeriod,
    Plan,
)


def _clp(n: int) -> str:
    """49990 -> '$49.990' (formato chileno, punto como separador de miles)."""
    return "$" + f"{n:,}".replace(",", ".")


def _workers_limit(plan: Plan) -> str:
    lim = PLAN_LIMITS[plan].max_active_workers
    return "sin límite" if lim is None else f"hasta {lim}"


def _projects_limit(plan: Plan) -> str:
    lim = PLAN_LIMITS[plan].max_active_projects
    return "ilimitadas" if lim is None else f"{lim}"


def _plans_block() -> str:
    """Bloque de planes generado desde plans.py."""
    pro_m = PLAN_PRICES_CLP[(Plan.PRO, BillingPeriod.MONTHLY)]
    pro_a = PLAN_PRICES_CLP[(Plan.PRO, BillingPeriod.ANNUAL)]
    emp_m = PLAN_PRICES_CLP[(Plan.EMPRESA, BillingPeriod.MONTHLY)]
    emp_a = PLAN_PRICES_CLP[(Plan.EMPRESA, BillingPeriod.ANNUAL)]
    return f"""PLANES Y PRECIOS (en pesos chilenos, CLP):

El cobro es por BANDA de "trabajadores activos" (trabajadores marcados como activos y
asignados a una faena activa). Los supervisores y todo el historial son ILIMITADOS en
todos los planes, incluido el gratis.

- {PLAN_DISPLAY_NAME[Plan.FREE]} — GRATIS. {_workers_limit(Plan.FREE)} trabajadores activos, {_projects_limit(Plan.FREE)} faena activa. Ideal para probar.
- {PLAN_DISPLAY_NAME[Plan.PRO]} — {_clp(pro_m)}/mes o {_clp(pro_a)}/año (2 meses gratis al pagar anual). {_workers_limit(Plan.PRO)} trabajadores activos, faenas {_projects_limit(Plan.PRO)}.
- {PLAN_DISPLAY_NAME[Plan.EMPRESA]} — {_clp(emp_m)}/mes o {_clp(emp_a)}/año. {_workers_limit(Plan.EMPRESA)} trabajadores activos, faenas {_projects_limit(Plan.EMPRESA)}.
- {PLAN_DISPLAY_NAME[Plan.ENTERPRISE]} — Sin límites, a cotización (para más de 500 trabajadores). Para esto conviene tomar los datos y derivar al equipo comercial.

Los planes Pro y Empresa se contratan directo en la plataforma, con {TRIAL_PERIOD_DAYS} días de prueba
gratis. Durante el lanzamiento los precios son referenciales."""


QUE_ES = """QUÉ ES RECONTRATA:

Recontrata es una plataforma para contratistas de minería y construcción que registra el
desempeño de los trabajadores en cada faena, para decidir con datos —y no de memoria— a
quién conviene volver a contratar en el próximo proyecto.

Es 100% chileno, funciona desde el celular en terreno (incluso sin señal, offline) y se
apega a la Ley 21.719 de protección de datos."""


EL_PROBLEMA = """EL PROBLEMA QUE RESUELVE:

En faena, el contrato es por obra o faena: cuando el proyecto termina, la relación termina
y la información de quién rindió bien SE PIERDE. La próxima vez que hay que armar una
cuadrilla, la decisión se toma de memoria del jefe de obra, por WhatsApp, o con listas
informales. No queda registro del rendimiento, la asistencia, los incidentes de seguridad
ni la razón de no recontratar a alguien.

Existen sistemas para saber si un trabajador PUEDE entrar a la faena (acreditación), pero
ninguno responde si DEBERÍA volver. Ese es justo el hueco que llena Recontrata."""


COMO_FUNCIONA = """CÓMO FUNCIONA:

1. Registras a tus trabajadores y tus faenas (proyectos).
2. Al cierre de cada faena, los supervisores evalúan a cada trabajador en 5 dimensiones:
   Calidad, Seguridad, Puntualidad, Trabajo en Equipo y Habilidad Técnica, más una
   recomendación de si lo recontratarías.
3. Recontrata calcula un puntaje PONDERADO por industria (en minería/construcción la
   Seguridad pesa más), y arma la ficha de cada trabajador: su puntaje, su tendencia en el
   tiempo y su historial entre faenas.

Así, al armar la próxima cuadrilla, sabes a quién conviene recontratar con datos reales.
El trabajador tiene su propio portal y derecho a réplica, cumpliendo la ley."""


COMO_EMPEZAR = """CÓMO EMPEZAR:

Se entra en recontrata.cl. Cualquiera puede crear una cuenta y partir con el plan Gratis
para probar, o tomar 14 días de prueba de un plan de pago. No se necesita instalar nada:
funciona en el navegador y en el celular."""


FAQ = """DUDAS FRECUENTES:

- "¿Sirve si tengo pocos trabajadores?" Sí, el plan Gratis permite hasta 15 activos.
- "¿Reemplaza la acreditación (SIGA, etc.)?" No, es complementario: la acreditación dice si
  puede entrar; Recontrata dice si conviene recontratarlo.
- "¿Es legal guardar evaluaciones de trabajadores?" Sí, cumpliendo la Ley 21.719: el
  trabajador es informado, tiene portal propio y derecho a réplica. No es una lista negra.
- "¿Funciona sin internet en faena?" Sí, se puede evaluar offline y sincroniza al recuperar
  señal."""


KNOWLEDGE_BASE = "\n\n".join(
    [QUE_ES, EL_PROBLEMA, COMO_FUNCIONA, _plans_block(), COMO_EMPEZAR, FAQ]
)
