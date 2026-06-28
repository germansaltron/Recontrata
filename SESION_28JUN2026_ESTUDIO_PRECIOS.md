# Sesión 28 jun 2026 — Estudio de precios con lente de inversor

> Registro de lo realizado. Producto: **Recontrata** (ex-FaenaScore).
> Carpeta: `C:\Users\JEF_INT\Claude Code German\FaenaScore`.

---

## 1. Contexto y objetivo

La sesión "Recontrata" se cerró por error. Al retomar, el hilo de trabajo era una pregunta del usuario:
**"Como inversor experto que estudia Recontrata y pide el estudio de cómo se hizo el pricing, ¿qué querría ver para convencerse de que estuvo bien hecho?"**

De esa conversación surgieron **7 puntos** que un inversor exige en un estudio de pricing:
1. Precio derivado del **valor** (value-based), no del costo.
2. Evidencia de **willingness-to-pay** revelada, no inferida.
3. **Value metric** correcto + expansion revenue.
4. **Benchmarking competitivo** real y honesto.
5. **Unit economics** (LTV, CAC, payback, margen).
6. **Sensibilidad y escenarios**.
7. **Coherencia** entre el estudio de precios y el producto.

Objetivo final: producir un estudio de mercado de precios que cubra los 7 puntos, **con fuentes verificadas y señalizadas** para verificación posterior.

---

## 2. Investigación realizada (4 agentes en paralelo, fuentes consultadas 27–28 jun 2026)

Se lanzaron 4 líneas de investigación web simultáneas:
- **Competidores Chile** (Buk, Talana, Rankmi, Nubox, Defontana, GeoVictoria) → modelo de cobro + precios.
- **Competidores globales** (Workyard, Connecteam, BambooHR, Lattice, 15Five, Rhumbix, Riskcast, Arcoro, Procore).
- **Benchmarks de pricing SaaS** (conversión trial/freemium, LTV:CAC, payback, NRR, Van Westendorp, captura de valor, activación).
- **Dimensionamiento mercado Chile** (empresas construcción, trabajadores, rotación, costo de mala contratación, sueldos, marco legal Ley 20.123 / listas negras / Ley 21.719).

Cada dato quedó etiquetado: 🟢 CONFIRMADO / 🟡 APROXIMADO / 🔴 NO VERIFICABLE / ⚙️ DERIVADO.

---

## 3. Entregables creados

| Archivo | Ubicación | Descripción |
|---|---|---|
| `ESTUDIO_PRECIOS_INVERSOR.md` | repo FaenaScore | Estudio completo (12 secciones) que cubre los 7 puntos, con tabla maestra de ~35 fuentes y sistema de confianza. |
| `Recontrata - Estudio de Precios (Inversor).docx` | `C:\Users\JEF_INT\Downloads\` | Versión Word del estudio (52 KB, 7 tablas). Generado con python-docx. Pendiente opcional: convertir URLs en hipervínculos clicables. |
| `SESION_28JUN2026_ESTUDIO_PRECIOS.md` | repo FaenaScore | Este documento. |

---

## 4. Hallazgos clave (lo nuevo que no estaba en el material previo)

1. **🔴 Cifra de ROI mal anclada.** `JUSTIFICACION_FAENASCORE.md` dice "reemplazar un trabajador cuesta ~50% del sueldo anual (~$750K CLP)". Es inconsistente: $750K como 50% anual implica sueldo de ~$125K/mes, **bajo el mínimo legal**. Recalculado con sueldo base construcción **~$785.349/mes** (CChC, mar-2024) → costo real por reemplazo **~$4,7M CLP** (~6× el número interno). **El error subestimaba el valor; corregido, el caso mejora.**

2. **🔴 Riesgo legal que toca el moat.** El activo defensivo (dato histórico compartido entre empresas) roza la prohibición de **"listas negras"** de la DT (**ORD N°1782/30, 10-abr-2015**, confirmado oficial) + **Ley 21.719** de datos personales (vigencia plena dic-2026). Implicancia de pricing: el plan **Enterprise/multi-empresa NO puede venderse como red de reputación compartida**; debe ser multi-faena *dentro de un mismo empleador/holding*. Requiere validación legal antes de construir ese plan.

3. **🔴 Precio de GeoVictoria no confirmado.** El rumor "$1.000–2.500 CLP/trabajador/mes" no aparece en ninguna fuente chilena. Única ancla: GeoVictoria España "desde 2 €/usuario/mes". Cualquier comparación en un pitch debe marcarse como estimación sujeta a cotización.

4. **Tres cifras "de pasillo" descartadas por no verificables** (no citar como duras): "65% de SaaS PLG usa híbrido"; "captura 10–25% del valor" como benchmark medido; "activación predice conversión 3–5× sobre el precio" (el 3–5× real es de *retención*, no de conversión vs. precio).

5. **Datos del dolor SÍ confirmados con fuente oficial:** rotación construcción **50,0%** (INE, jun-2024, la más alta de Chile); **712 mil** ocupados en construcción (CChC/INE, ago-2025); **88.675** empresas de construcción (SII vía agregador).

---

## 5. Recomendación de precios (conclusión del estudio)

El estudio **valida la tabla ya decidida** y sugiere que hay *headroom* hacia arriba, no hacia abajo:

| Plan | Trabajadores activos | Mensual | Anual (2 meses gratis) |
|---|---|---|---|
| Gratis "Capataz" | 15 · 1 proyecto | $0 | $0 |
| **Pro "Faena"** ⭐ | hasta 100 · proyectos ilimitados | **$49.990** | $499.900 |
| Empresa "Contratista" | hasta 500 · multi-faena | **$149.990** | $1.499.900 |
| Enterprise | +500 | Cotización | Contrato anual |

En todos: supervisores ilimitados + histórico ilimitado.

- **$49.990 ≈ $0,53/trabajador/mes** → un orden de magnitud bajo los per-user globales ($8–16). Hay espacio de precio.
- Unit economics (modelados): **LTV:CAC ~6:1**, **payback ~9,8 meses**, margen 82% (supuestos marcados).
- Antes de subir: correr test de precio **$39.990 / $49.990 / $69.990** con Van Westendorp/Gabor-Granger.

---

## 6. Pendientes / próximos pasos (priorizados por el estudio)

1. **🔴 WTP revelada:** convertir 3–5 design partners en ingreso real (precio fundador –50%). Gap #1.
2. **🔴 Validación legal** del modelo de datos (listas negras / Ley 21.719) → define qué se vende en planes superiores.
3. **🟠 Billing + enforcement** de límites de plan (hoy no existe; los planes son vitrina, verificado en QA 26-jun).
4. **🟡 TAM/SAM/SOM bottom-up** con el .xlsx oficial del SII (desglose construcción por tamaño).
5. **🟡 Cotizaciones reales** de GeoVictoria/Buk/Talana para fijar el ancla de precio local.
6. **Coherencia documental:** corregir la cifra de ROI ($750K → ~$4,7M) en `JUSTIFICACION_FAENASCORE.md` y `PROPUESTA_MONETIZACION.md`. **(Pendiente de decisión del usuario.)**
7. **Opcional:** hipervínculos clicables en el .docx.

---

---

## 7. Adenda — clarificación del criterio de costo y reanclaje a minería (28 jun 2026)

Tras una primera versión, el usuario pidió dos cosas: (a) que quedara muy claro de dónde sale el criterio "50% del salario anual = costo de reemplazo", y (b) re-anclar el estudio en minería (no construcción). Ambas se ejecutaron con investigación verificada adicional.

### 7.1 Criterio de costo de reemplazo — corregido y trazado
- Se rastreó la **fuente primaria**: el "50%" NO estaba bien fundado. La evidencia académica primaria es **Center for American Progress (Boushey & Glynn, 2012)**, meta-análisis de 30 case studies: costo de reemplazo ≈ **20% del salario anual** (16% para sueldos <US$30k), NO 50%.
- El "50–200%" de Gallup/SHRM es una estimación "all-in" que aplica a cargos profesionales/gerenciales, no a operativos. SHRM además resultó **NO VERIFICABLE** (sin fuente primaria localizable).
- **Corrección en el estudio (Sección 1):** costo de reemplazo de operario construcción **~$1,5M** (16% de $9,42M; el operario chileno cae en el tramo "<US$30k/año" de CAP), no ~$4,7M ni ~$750K. Reencuadre clave: el valor de Recontrata NO es la rotación, es el **diferencial bad-rehire + riesgo de seguridad minero**.

### 7.2 Reanclaje a minería (beachhead) + construcción (TAM)
Nueva **Sección 1-BIS** en el estudio. Hallazgos verificados:
- **Rotación minería 18,6% vs construcción 50,0%** (INE jun-2024, confirmado). Matiz: el contratista de faena suele clasificarse fuera del CIIU minería, así que el 18,6% subestima su rotación real.
- **% de contratistas en gran minería = ~75%** (no 55-60%, que era dato de ~2008). Fuente: CCM-Eleva/Consejo Minero. **Corrige el dato heredado de `JUSTIFICACION_FAENASCORE.md`.**
- **Minería = sector mejor pagado de Chile** (~$2,31M imponible promedio). Operativos faena ~$930K–$2,25M.
- **Valor del riesgo minero:** un incidente puede paralizar la faena (US$ millones/día; caso El Teniente jul-2025, 6 fallecidos, paralización SERNAGEOMIN), con responsabilidad solidaria de la mandante (Art. 66 bis Ley 16.744 + DS 76). Accidentabilidad minera baja (1,0 vs 3,1 construcción) pero de altísima severidad.
- **Cultura de acreditación instalada:** SICEP (~3.300–3.800 empresas acreditadas / ~8.000 proveedores APRIMIN) → menos cambio de hábito, mayor WTP.
- **TAM doble capa (Sección 9 actualizada):** SAM minero ~US$4,8M (3.800 SICEP × ARPA premium ~$1,2M) + SAM construcción ~US$5,9M; SOM año 1–2 ~US$95–145K.
- **Implicación de pricing:** minería soporta precio premium; evaluar un tier "Minería" explícito una vez revelada la WTP.

### 7.3 Entregables actualizados
- `ESTUDIO_PRECIOS_INVERSOR.md` — actualizado (Secciones 0, 1, 1-BIS, 9, 10, 11, 12).
- `Recontrata - Estudio de Precios (Inversor) v2.docx` en Downloads (226 párrafos, 9 tablas). **Nota:** la v1 quedó bloqueada (abierta en Word); v2 es la versión vigente.

### 7.4 Correcciones de coherencia aplicadas (28 jun, autorizadas por el usuario)
Se propagaron las dos correcciones de datos a TODO el contenido que mira el cliente:
- **Costo de reemplazo:** "$750K / 50%" → **~$1,5M (16-20%, CAP 2012)** en: `JUSTIFICACION_FAENASCORE.md` (2.3), `PROPUESTA_MONETIZACION.md` (ROI), `Landing.tsx` (hero + stat-bar + ROI del plan), y el **guion + pipeline del video clip1** (narración y subtítulos).
- **% contratistas minería:** "55-60%" → **~75%** en `JUSTIFICACION_FAENASCORE.md`.
- **Pricing en `JUSTIFICACION` (6.1):** tabla vieja ($39.000/$99.000/$249.000) → tabla decidida (Gratis/$49.990/$149.990/Enterprise).
- **ROI recalculado** y consistente en todos los docs: evitar 3 malas recontrataciones (~$1,5M c/u) ahorra ~$4,5M vs ~$600K/año del plan → **ROI sobre 7×**.
- La landing **ya tenía los precios nuevos** y la cifra de rotación 50% construcción (INE) es correcta — no se tocaron.

**Video — pendiente de acción (requiere tu OK):** el clip1 (.mp4 en YouTube oculto) tiene la narración vieja ("casi un millón"). El guion y el pipeline (`produce_clip1.py`) ya están corregidos, pero **re-renderizar implica costo de OpenAI TTS + re-captura del sitio con Playwright + re-subir a YouTube**. No se ejecutó; queda a la espera de autorización.

### 7.5 Pendientes restantes
- Los design partners deben ser **contratistas mineros**, no construcción genérica.
- Refinar SAM con `.xlsx` del SII (construcción por tamaño) + **Barómetro SICEP 2025** (proveedores mineros por tamaño/región).
- Re-renderizar y re-subir el video clip1 (ver arriba) cuando se autorice.
- Docs internos (`PROGRESS.md`, `PLAN_ACCION_CLASE_MUNDIAL.md`) conservan menciones históricas a "$750K" como registro de lo que se construyó; no se modifican por ser bitácoras.

---

*Documento generado el 28 de junio de 2026; adenda el mismo día.*
