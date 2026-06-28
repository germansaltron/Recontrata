# FaenaScore — Propuesta de Monetización

> Investigación de competidores + recomendación de modelo y precios.
> Fecha: 30 de mayo 2026 · Autor: análisis para Germán / Faymex
> Estado: borrador para decisión. Los precios de competidores marcados con (~) son aproximados y conviene re-confirmarlos antes de usarlos en material externo.

---

## 0. Recomendación en una línea

**Cobra por banda de "trabajadores activos" (flat tiers), con supervisores ilimitados, históricos ilimitados gratis, y un modelo híbrido freemium + trial de 14 días.** Sube el plan Pro de $29.990 a ~$49.990 CLP/mes. El cuello de botella de adopción en este mercado no es el precio: es la confianza y el cambio de hábito. Cobrar barato no acelera la venta y deja plata sobre la mesa.

---

## 1. Hallazgos de la investigación

### 1.1 Competidores en Chile — el eje de cobro dominante es "por trabajador/mes"

| Producto | Categoría | Modelo de cobro | Nota para FaenaScore |
|---|---|---|---|
| **Buk** | Suite RRHH (oficina) | **Por colaborador/mes**, variable y modular. "Gestión del Desempeño" es módulo aparte. Precio solo por cotización. | Define la convención que tu cliente ya conoce: se paga por cabeza/mes. Enfocado a planilla formal, no a faena temporal. |
| **Talana** | Suite RRHH + asistencia | Por colaborador/mes, modular. Fuerte en control de asistencia móvil. | Mismo eje. Compite en asistencia, no en desempeño de terreno. |
| **Rankmi** | Gestión de personas / desempeño | Por colaborador/mes, enterprise, sin precio público. | El más cercano en "desempeño", pero para empleados fijos de empresa mediana-grande, no temporales de faena. |
| **Nubox / Defontana** | Contabilidad + remuneraciones PYME | Por planes/rangos, más barato. | Refleja el piso de disposición a pagar de la PYME chilena. |
| **GeoVictoria** | Control de asistencia terreno | Por trabajador/mes (~$1.000–2.500 c/u). | Tu competidor **adyacente** más relevante: ya atiende faena. Mismo eje de cobro. |
| **Validate / SIGA / Ctrl / Prevsis** | Acreditación y cumplimiento Ley 20.123 | Por empresa subcontratista o por mandante. | Responden "¿puede ENTRAR a la faena?", no "¿debería VOLVER?". Es el gap que FaenaScore ocupa. |

**Conclusión Chile:** no hay competencia directa (ya documentado en `JUSTIFICACION_FAENASCORE.md`), pero **todo el ecosistema cobra por trabajador/mes**. Salirte de ese eje genera fricción de comprensión en la venta. La banda flat por trabajadores es la traducción "sin fricción" de ese eje.

### 1.2 Competidores globales (construction / workforce / performance)

| Producto | País | Modelo de cobro | Precio (~) |
|---|---|---|---|
| **Workyard** | USA | Per-user/mes **+ base fee fijo** | ~US$6–8 (Starter) / US$13–16 (Pro) por usuario + **US$50/mes base** · trial 14 días |
| **Connecteam** | Israel | Flat por banda (primeros ~30 users), free hasta ~10 | Plan pago desde ~US$29–35/mes por las primeras 30 personas |
| **BambooHR** | USA | Per-employee/mes; Performance es **add-on** | ~US$6–12/empleado |
| **Lattice** | USA | Per-person/mes (desempeño) | ~US$11/persona + add-ons |
| **15Five** | USA | Per-user/mes | ~US$4 (engage) a US$10–16 (plataforma) |
| **Rhumbix / Riskcast / Arcoro** | USA | Enterprise, per-project o per-user, sin precio público | Venta consultiva |
| **Procore** | USA | % del volumen de obra (ACV) | Enterprise caro |

**Dos aprendizajes accionables:**
1. **El base fee de Workyard es criticado** justo por empresas chicas con fuerza laboral fluctuante. FaenaScore atiende exactamente ese perfil (rotación 50%) → **no copies el base fee**; un flat por banda es más amable.
2. **Performance casi siempre es un add-on o producto separado**, no el core. FaenaScore tiene la ventaja de ser un producto *enfocado* en eso (no un módulo escondido en una suite cara).

### 1.3 Modelo de pricing para SaaS B2B en etapa temprana

- **El "value metric" debe alinearse con el valor que el cliente recibe.** En FaenaScore el valor crece con el **número de trabajadores gestionados** (más memoria institucional, más decisiones de recontratación informadas), no con el número de supervisores. → El eje correcto es **trabajadores**, no seats.
- **No cobres por supervisor (seat).** El activo defensivo de FaenaScore es **el dato acumulado**. Cobrar por seat penaliza justo el comportamiento que genera el dato (que muchos supervisores evalúen). Supervisores ilimitados.
- **Flat tiers > per-unit puro para empezar.** Más simple de vender, ingreso predecible, evita la fricción de "contar cabezas" mes a mes con rotación alta. La banda actúa como proxy del per-worker sin su fricción.
- **Históricos ilimitados gratis.** El histórico ES el moat; cobrarlo desincentiva acumularlo. Cobra por **capacidad operativa actual** (trabajadores activos en los últimos ~90 días o en proyectos activos), no por el acumulado histórico.

### 1.4 Freemium vs free trial (datos de la investigación)

- Trial: **14–25% de conversión trial→pago** en B2B; óptimo **14 días**; ramp de MRR más rápido en etapa temprana.
- Freemium: solo **2–5% free→pago**, ramp lento (90–180 días), pero el gate de uso genera un gatillo emocional fuerte ("quiero mantener lo que ya tengo").
- **Híbrido (freemium de captación + trial del plan pago)** = estrategia más usada en 2026 (~65% de SaaS PLG).
- **La activación es el predictor #1** de conversión (3–5x), por encima del precio.

**Matiz específico de FaenaScore:** el "momento ajá" no ocurre en la primera faena (cuando solo *ingresas* evaluaciones), sino al **armar la SEGUNDA cuadrilla** y poder filtrar por desempeño histórico. Eso tarda más de 14 días. Por eso:
- **Freemium** para que el dato se acumule sin costo y llegue ese segundo momento (crea switching cost).
- **+ Trial de 14 días del plan Pro** para el contratista que ya tiene varias faenas y quiere todo ya.

---

## 2. El eje de cobro correcto para FaenaScore

| Eje candidato | A favor | En contra | Veredicto |
|---|---|---|---|
| Per-seat (supervisor) | Simple, predecible | Subcaptura valor (pocos supervisores, muchos trabajadores); **penaliza la adopción que genera el moat** | ❌ No |
| Per-worker exacto/mes | Alinea con valor y con convención chilena | Fricción de conteo con rotación 50%; cobrar por temporal que ya se fue es raro | ⚠️ Como base conceptual, sí; como factura mensual, no |
| Per-project | Alinea con el flujo (eval al cierre) | Ingreso lumpy e impredecible | ❌ No como eje principal |
| **Flat por banda de trabajadores activos** | Simple, predecible, traduce el eje "trabajador" sin fricción, supervisores ilimitados | Hay que definir bien las bandas | ✅ **Recomendado** |

---

## 3. Propuesta de planes y precios (CLP)

Eje: **trabajadores activos** (en proyectos activos / últimos 90 días). **Supervisores ilimitados. Historial ilimitado en todos los planes.**

| Plan | Trabajadores activos | Precio mensual | Precio anual (2 meses gratis) | Para quién |
|---|---|---|---|---|
| **Gratis** ("Capataz") | Hasta **15** · 1 proyecto activo | $0 | $0 | Que un jefe de obra lo pruebe en UNA faena sin pedir permiso. Captación + activación. |
| **Pro** ("Faena") ⭐ | Hasta **100** · proyectos ilimitados | **$49.990** | $499.900 (~$41.660/mes) | Contratista chico-mediano. Caballo de batalla. Búsqueda/filtros avanzados, export, alertas. |
| **Empresa** ("Contratista") | Hasta **500** · multi-faena | **$149.990** | $1.499.900 (~$124.990/mes) | Contratista grande. API, insights IA, onboarding, soporte prioritario. |
| **Enterprise** | +500 / multi-empresa | Cotización | Contrato anual | SSO, integraciones (acreditación), datos a medida. |

### Justificación de los números

- **Argumento de ROI (úsalo en la venta):** evitar **1 sola** mala recontratación al año ahorra ~$1,5M CLP (≈16-20% del sueldo anual de reemplazar a un operativo). El plan Profesional cuesta ~$600.000/año. **ROI ~2,5x con una sola decisión correcta**; con 3, supera 7x — y mucho más si se evita un incidente de seguridad o la pérdida de un contrato en faena minera.
  - **Fuente del criterio (≈16-20%):** Center for American Progress (CAP), instituto de políticas públicas de EE.UU.; estudio de Boushey & Glynn (2012), meta-análisis de 30 case studies. *Reemplaza la cifra previa de "$750K / 50%", que no tenía fuente y estaba mal anclada.* Consultable: https://www.americanprogress.org/article/there-are-significant-business-costs-to-replacing-employees/
- **Por qué subir Pro de $29.990 → $49.990:** en venta industrial B2B, $30k vs $50k no cambia la decisión (no son sensibles al precio a ese nivel; son sensibles a si funciona y si genera fricción). Un precio muy bajo **señaliza "poco serio"** en un rubro acostumbrado a pagar Buk/GeoVictoria por cabeza. $49.990 sigue cómodo bajo el umbral psicológico de "decisión gerencial pesada" (~$150k+).
- **Contexto de gasto del cliente:** un contratista con 50 trabajadores ya paga ~$75.000/mes solo en control de asistencia (GeoVictoria a ~$1.500 c/u). FaenaScore a $49.990 es un gasto incremental menor y fácil de justificar.
- **Empresa a $149.990** (no $249.000 del doc original): mantiene el salto 3x respecto a Pro sin entrar en zona de ciclo de venta largo; deja $249k+ para Enterprise con contrato.

### Formas de pago (críticas en B2B chileno)
- **Transferencia + factura** (muchas PYMEs pagan así, a 30 días) — imprescindible.
- **Webpay / tarjeta** (Transbank) para self-serve.
- **Anual con descuento** (2 meses gratis) mejora caja y retención.

---

## 4. Estrategia freemium + trial (híbrida)

1. **Free plan diseñado para LAND, no para quedarse:** 15 trabajadores + 1 proyecto. Un contratista real supera eso apenas lo usa en serio → upgrade natural. El histórico no se borra al pasar de free a pago (refuerza switching cost).
2. **Trial de 14 días del plan Pro** para quien ya quiere filtros/insights desde el día 1.
3. **Optimiza activación, no precio:** define el "momento ajá" (armar la 2ª cuadrilla filtrando por score) y empuja al usuario hacia él con onboarding guiado. Es el predictor #1 de conversión.
4. **Gate emocional:** cuando el free llega al límite de 15 trabajadores en plena faena, el mensaje es "no pierdas el historial que ya construiste" — gatillo más potente que cualquier email.

---

## 5. Go-to-market inicial (eres categoría naciente, no hay demanda en Google todavía)

1. **Faymex como caso 0** (dogfooding): evaluá tus últimas faenas, genera el testimonio con números reales de ahorro. Sin esto no hay venta consultiva creíble.
2. **5–10 design partners** de la red de Germán: **precio fundador –50% de por vida** a cambio de feedback + testimonio. Lock-in de tarifa.
3. **Venta 1:1 consultiva**, no self-serve aún. Demo + onboarding asistido. El mercado no busca esto solo todavía → hay que crear la categoría.
4. **Ángulo de cumplimiento DT:** "reemplaza las listas negras ilegales por un sistema legal, transparente y en tu Reglamento Interno". Es un gancho de venta + un argumento de riesgo evitado.
5. **Bundle futuro** con AcreditaMinero (acreditación + desempeño = suite): "¿quién puede entrar Y quién debería volver?".

---

## 6. Comparación con el pricing tentativo actual

| | Tentativo actual | Propuesta |
|---|---|---|
| Eje de cobro | Flat (implícito) | Flat **por trabajadores activos**, seats ilimitados, histórico ilimitado |
| Free | $0 | $0 (15 trabajadores / 1 proyecto, definido para land) |
| Pro | $29.990 | **$49.990** (subir) |
| Empresa | $99.990 | **$149.990** |
| Enterprise | — | Cotización (+500) |
| Conversión | — | Híbrido freemium + trial 14d, optimizar activación |
| Pago | — | Transferencia+factura, Webpay, anual –17% |

---

## 7. Decisiones tomadas (Germán, 30 may 2026) ✅

1. **Plan Pro a $49.990 CLP/mes** — confirmado (subir desde el tentativo $29.990).
2. **Eje de cobro: "trabajadores activos" con supervisores ilimitados** — confirmado. Histórico ilimitado en todos los planes.
3. **Conversión: híbrido freemium + trial de 14 días** — confirmado.
4. **10 design partners** con precio fundador –50% de por vida — confirmado.

### Tabla de precios FINAL (decidida)

| Plan | Trabajadores activos | Mensual | Anual (2 meses gratis) |
|---|---|---|---|
| Gratis "Capataz" | 15 · 1 proyecto | $0 | $0 |
| **Pro "Faena"** ⭐ | hasta 100 · proyectos ilimitados | **$49.990** | $499.900 |
| Empresa "Contratista" | hasta 500 · multi-faena | **$149.990** | $1.499.900 |
| Enterprise | +500 | Cotización | Contrato anual |

### Próximos pasos de implementación (no de decisión)
- [ ] Actualizar la sección de pricing de la landing (`frontend/src/pages/Landing.tsx`): hoy dice Gratis/$29.990/$99.990 → cambiar a Gratis/$49.990/$149.990 con copy "trabajadores activos" y supervisores ilimitados.
- [ ] Reflejar límites de plan (15 trabajadores en free) en el producto cuando se construya el billing.
- [ ] Diseñar el flujo de design partners (–50% lifetime, primeros 10).
- [ ] Definir/añadir transferencia+factura y Webpay como medios de pago cuando se active el cobro.

---

## Fuentes consultadas
- [Buk — precios](https://www.buk.cl/precios) · [Comparativa softwares RRHH Chile 2026](https://www.buk.cl/blog/mejores-softwares-recursos-humanos-chile)
- [Talana](https://web.talana.com/) · [Talana en Capterra](https://www.capterra.com/p/220139/Talana/)
- [Workyard — pricing](https://www.workyard.com/pricing) · [Workyard pricing guide (GetApp)](https://www.getapp.com/hr-employee-management-software/a/workyard/pricing/)
- [Freemium vs Free Trial (Dodo Payments)](https://dodopayments.com/blogs/saas-free-trial-vs-freemium) · [SaaS trial conversion benchmarks (First Page Sage)](https://firstpagesage.com/seo-blog/saas-free-trial-conversion-rate-benchmarks/) · [Freemium vs trial (Sybill)](https://www.sybill.ai/blogs/freemium-vs-free-trial)
- Base interna: `JUSTIFICACION_FAENASCORE.md` (panorama competitivo Chile/LATAM, ROI, marco legal).

> Nota: los precios de competidores marcados (~) provienen de búsqueda web del 30-may-2026 y de conocimiento de mercado; los planes chilenos (Buk/Talana/Rankmi) no publican tarifas exactas (solo cotización). Re-confirmar antes de usar en material comercial externo.
