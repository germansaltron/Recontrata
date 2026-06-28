# Recontrata — Estudio de Mercado de Precios (lente de inversor)

> Cómo se construyó el pricing de Recontrata y por qué resiste un análisis de inversión.
> Fecha de elaboración: 28 de junio de 2026 · Autor: análisis para Germán / Faymex
> Documento complementario de `PROPUESTA_MONETIZACION.md` (decisión) y `JUSTIFICACION_FAENASCORE.md` (problema/mercado).
> Producto antes llamado FaenaScore; en este documento se usa **Recontrata**.

---

## Cómo leer este documento (sistema de verificación de fuentes)

Cada dato externo lleva una etiqueta de confianza, pensada para que un tercero (inversor, due diligence) pueda **re-verificar** sin rehacer la investigación:

| Etiqueta | Significado | Cómo verificar |
|---|---|---|
| 🟢 **CONFIRMADO** | Dato de fuente oficial o reputada, leído directamente en la fuente primaria. | Abrir la URL citada; el dato está ahí. |
| 🟡 **APROXIMADO** | Dato real pero proveniente de comparador secundario (Capterra/GetApp/G2/blogs reputados) o de fuente oficial accedida vía tercero. Orden de magnitud confiable, cifra exacta sujeta a confirmación. | Abrir URL; cruzar con una segunda fuente antes de usar en material externo. |
| 🔴 **NO VERIFICABLE** | No existe fuente pública que lo confirme (precio solo por cotización, o cifra que circula en blogs sin fuente primaria). | Requiere acción: pedir cotización, descargar PDF de pago, o **no usar como dato duro**. |
| ⚙️ **DERIVADO** | Cálculo propio a partir de datos etiquetados arriba. La aritmética es auditable; los supuestos están marcados. | Recalcular con los inputs citados. |

**Fecha de consulta de todas las fuentes web: 27–28 de junio de 2026.** Los precios SaaS cambian; re-confirmar antes de usar cifras de competidores en material comercial o de levantamiento de capital. La tabla maestra de fuentes está en la **Sección 11**.

**Tres cifras "de pasillo" que NO sobrevivieron la verificación** (las menciono arriba para que nadie las cite como duras): el "65% de SaaS PLG usa modelo híbrido", el "10–25% de captura de valor" como benchmark medido, y el "activación predice conversión 3–5× sobre el precio". Detalle en Secciones 2, 4 y 8. Que el estudio las descarte explícitamente es, en sí, una señal de rigor.

---

## 0. Resumen ejecutivo para el inversor

**Tesis de pricing:** Recontrata cobra por **trabajadores activos** (no por asiento de supervisor), con planes flat por banda, freemium de captación + trial de 14 días, y un plan ancla Pro de **$49.990 CLP/mes**. El método para llegar a ese precio es value-based (derivado del diferencial de valor que el producto ayuda a capturar), triangulado contra el eje de cobro dominante del mercado chileno (todos cobran "por cabeza/mes") y contra benchmarks globales de performance-SaaS.

**Sector ancla (Sección 1-BIS):** el beachhead es el **contratista minero** (mayor sueldo, mayor riesgo evitado, cultura de acreditación ya instalada vía SICEP), y la expansión de volumen es **construcción**. El estudio cuantifica el valor en minería y dimensiona el TAM en ambos.

**Lo que está sólido (verificable):**
- El **dolor está cuantificado con fuente oficial**: construcción rota 50,0% (la más alta de Chile) y minería 18,6% (INE, 🟢); la gran minería emplea ~75% de su fuerza laboral vía contratistas (Consejo Minero/CCM-Eleva, 🟢) sobre ~305 mil de empleo directo. El mercado existe y es medible.
- El **eje de cobro es una decisión argumentada**, no un default: se descartaron per-seat, per-worker exacto y per-project con razones (Sección 3), y el eje elegido genera expansion revenue natural.
- El **benchmarking competitivo es honesto**: distingue precio confirmado de estimado, y reconoce que el competidor de referencia (GeoVictoria) no publica tarifa.
- El **valor en minería es de otra magnitud**: el costo de un mal trabajador no es la rotación, sino la **paralización de faena** (US$ millones/día) y la **responsabilidad solidaria de la mandante** (🟢), riesgo que un regulador sectorial (SERNAGEOMIN) puede gatillar.

**Lo que un inversor debe exigir antes de creer el número (gaps reconocidos):**
1. **La cifra de costo-de-reemplazo no estaba bien fundada.** El doc interno usaba "50% del sueldo anual (~$750K)" sin fuente; la evidencia académica primaria (CAP 2012) dice **16–20%** para operativos, no 50%. Corregido (Sección 1) el valor por reemplazo queda en ~$1,5M (16%, el tramo de CAP que aplica al operario chileno), pero el caso *se fortalece* al reencuadrarse hacia el diferencial bad-rehire + riesgo de seguridad minero, que no depende de ese %.
2. **No hay willingness-to-pay revelada todavía**: el precio se sostiene en juicio del fundador, no en datos. El plan de obtenerla (design partners + Van Westendorp) está en Sección 3, pero a hoy es hipótesis.
3. **Unit economics modelados, no medidos**: sin clientes pagando, LTV/CAC/payback son proyección (Sección 6).
4. **Riesgo legal que toca el moat**: el activo defensivo (dato histórico compartido) roza la prohibición de "listas negras" de la DT (🟢 ORD 1782/30) y la nueva Ley 21.719 de datos personales (vigente dic-2026). El pricing del plan Enterprise/multi-empresa depende de resolver esto (Sección 8).
5. **El producto aún no puede cobrar**: no existe billing ni enforcement de límites de plan (verificado en QA, 26-jun-2026).

**Veredicto en una línea:** el *método* de pricing es defendible y por encima del promedio para una pre-seed; la *evidencia empírica* que lo respalda está pendiente y es la prioridad #1 de los próximos 90 días.

---

## 1. Punto 1 — El precio se deriva del VALOR, no del costo

### 1.1 De dónde sale el criterio "costo de reemplazo = X% del salario anual" (trazabilidad completa)

Esta es la pieza que un inversor cuestiona primero, así que se documenta su origen con fuente primaria. El número **no es arbitrario**, pero el "50%" que circulaba en el material interno **no estaba bien fundado para un trabajador operativo**. Hay dos familias de fuentes que miden cosas distintas:

> **¿Qué es CAP?** El **Center for American Progress** es un instituto de investigación de políticas públicas (*think tank*) de Estados Unidos, fundado en 2003 y con sede en Washington D.C. Su estudio de 2012 sobre el costo de rotación es el meta-análisis académico más citado del tema. **Consultable directamente:** artículo → https://www.americanprogress.org/article/there-are-significant-business-costs-to-replacing-employees/ · PDF con las cifras → https://www.americanprogress.org/wp-content/uploads/sites/2/2012/11/CostofTurnover.pdf

| Fuente | Cifra | Qué mide | Confianza | Verificación |
|---|---|---|---|---|
| **Center for American Progress** — Boushey & Glynn, 16-nov-2012. Meta-análisis de **30 case studies en 11 papers** (1992–2007) | **~20% típico del salario anual; 16,1% para sueldos <US$30k**; 21% excl. ejecutivos/médicos; hasta **213%** ejecutivos; rango 5,8%–213% | Sobre todo **costos directos** (solo 2 de 11 papers incluían indirectos) → es un **piso conservador** | 🟢 CONFIRMADO | PDF académico leído íntegro |
| **Gallup** — McFeely & Wigert, 13-mar-2019 | **"½ a 2× el salario" = 50%–200%** | Estimación **"all-in"** (directos + indirectos), sesgada a roles profesionales/gerenciales | 🟢 CONFIRMADO | Página primaria |
| **Work Institute** — Retention Report 2017 | **33%** (≈$15k sobre mediana $45k) | Directos + ocultos | 🟡 APROXIMADO-ALTO | HR Dive cita textual del reporte |
| **SHRM** | "50–200%" / "6–9 meses de salario" | All-in | 🔴 **NO VERIFICABLE** | Sin documento primario localizable; solo blogs |

**Cita textual primaria (CAP, 2012):** *"it costs businesses about one-fifth of a worker's salary to replace that worker"* y, explícitamente para bajos ingresos: *"The typical cost of turnover for positions earning less than $30,000 annually is 16 percent of an employee's annual salary."*

**Qué incluye ese costo (metodología, para que el número sea auditable):**
- **Costos directos (~16–20%):** publicar la vacante, reclutar, seleccionar, exámenes preocupacionales, verificación de antecedentes, inducción, capacitación, certificaciones, uniformes.
- **Costos indirectos (lo que lleva el número a 50%+):** productividad perdida del que se va, costo de la vacante, sobrecarga del equipo, **rampa del reemplazo (errores, re-trabajo, menor calidad)**, pérdida de conocimiento institucional.

**Veredicto honesto sobre el "50%":** CAP (~16–20%) y Gallup/SHRM (50–200%) **no se contradicen por error, sino por método**: CAP casi no cuenta indirectos; Gallup/SHRM sí, y además promedian cargos de mayor nivel. Para un **trabajador operativo / por hora**, lo defendible ante due diligence es **16–20% (CAP)**, no 50%. El "50%" interno tomaba el piso del rango all-in de Gallup/SHRM y lo aplicaba a un perfil al que ese rango **no corresponde**. CAP es explícito: el costo *"does become less significant for those with low earnings."*

### 1.2 Cuantificación corregida del costo de reemplazo

- Sueldo base promedio sector construcción: **~$785.349 CLP/mes** (CChC, Índice de Remuneraciones, mar-2024, 🟡). Anual ≈ **$9,42M CLP**.
- Criterio defendible para operativo: **16–20% del salario anual** (CAP, 🟢), con tope all-in ~40% (frontline, marco Gallup, 🟡).
- ⚙️ **DERIVADO:** costo de reemplazo de un operario de construcción ≈ 16–20% × $9,42M = **~$1,5M–$1,9M CLP**. Cifra headline conservadora **~$1,5M** (16%, el tramo "<US$30k/año" de CAP, que es donde cae el operario chileno: $9,42M ≈ US$9,9k); tope all-in ~40% = ~$3,8M. **Esto reemplaza el "~$4,7M / 50%" de versiones anteriores de este estudio, que estaba sobreestimado.**

### 1.3 El reencuadre que hace al caso MÁS fuerte (no más débil)

Corregir el número a la baja **no debilita la tesis**, porque el valor de Recontrata **nunca debió descansar en el costo de rotación genérico**:
- La rotación en faena es **estructural** (los contratos por obra/faena terminan por diseño); Recontrata no la evita.
- Lo que evita es **re-contratar a un trabajador *conocido-malo***. El valor relevante es el **diferencial entre un buen y un mal trabajador**: re-trabajo, **incidentes de seguridad** y —en faena minera— **riesgo de perder el contrato con la mandante**. Ese diferencial es mayor que cualquier "% del salario" y **no depende de la cifra discutible del 50%**.
- **En minería el diferencial se dispara:** un incidente fiscalizado por SERNAGEOMIN (DS 132) o la pérdida de un contrato con una mandante (Codelco/BHP/AMSA) cuesta **órdenes de magnitud más** que reemplazar a un trabajador. Por eso el ancla correcta del valor es **minería**: el caso deja de apoyarse en un % de rotación cuestionable y pasa a apoyarse en **riesgo de seguridad/contrato**, que es enorme y verificable. *(El reanclaje completo del estudio a minería —sueldos mineros, rotación del segmento contratista, TAM y tier premium— está en elaboración; ver `SESION_28JUN2026_ESTUDIO_PRECIOS.md`.)*

> **Conclusión Punto 1:** el método (value-based) es correcto, pero el *input numérico* del material previo estaba sobreestimado y mal citado. Corregido (CAP 16–20% para el reemplazo) y reencuadrado (valor = diferencial bad-rehire + riesgo de seguridad minero), el caso queda **mejor fundado y es más difícil de refutar**. Acción: medir el diferencial real con datos de Faymex (caso 0) en faena minera.

### 1.4 Captura de valor

- Plan Pro: **$49.990/mes = $599.880/año** (⚙️ DERIVADO).
- Un contratista con 100 trabajadores y 50% de rotación enfrenta ~50 decisiones de recontratación/año. Si Recontrata mejora aunque sea **una** de esas decisiones al año, el valor entregado (costo de reemplazo evitado **~$1,5M** + el diferencial de productividad/seguridad, que en minería es mucho mayor) ya supera holgadamente el costo anual del plan ($599.880). Con 3 decisiones corregidas al año (~$4,5M), el ROI es de **~7×** solo por costo de reemplazo, y **mucho mayor** si se incluye un incidente de seguridad o contrato evitado.
- **Sobre el "capturar 10–25% del valor":** la investigación encontró que **esa regla NO es un benchmark medido**, sino heurística de oficio (🔴 NO VERIFICABLE como cifra dura; LeveragePoint, fuente reputada de pricing, *rechaza* la idea de un porcentaje fijo y argumenta que es contextual, 🟢). Lo defendible: a $599.880/año contra un valor de varios millones, Recontrata captura **una fracción baja del valor que crea**, lo que deja **headroom de precio** y es señal de poder de fijación de precios, no de subcobro irracional.

> **Conclusión Punto 1:** el método es value-based y correcto en su lógica. La debilidad estaba en el *input numérico* (50% sobreestimado, sin fuente); corregido a 16–20% (CAP) y reencuadrado hacia el diferencial bad-rehire + riesgo de seguridad minero, el caso es más sólido. Acción: documentar el costo-por-evento y medirlo con datos de Faymex (caso 0) en faena minera.

---

## 1-BIS. El sector ancla: minería (beachhead) + construcción (TAM)

Las versiones iniciales de este estudio anclaron la aritmética en **construcción**, principalmente porque la estadística pública chilena es más limpia ahí (INE/CChC). Pero el cliente de **mayor disposición a pagar y menor fricción de venta es el contratista minero**. La estrategia correcta no es elegir uno, sino **doble ancla**: entrar por **minería** (alto valor, alta WTP, cultura de acreditación ya instalada) y expandir a **construcción** (volumen).

### 1-BIS.1 Por qué minería es el beachhead (datos verificados)

| Dimensión | Faena minera | Construcción general |
|---|---|---|
| **Sueldos** (→ costo de reemplazo y presupuesto del cliente) | **Sector mejor pagado de Chile**: ingreso imponible promedio **~$2,31M/mes** (Sup. de Pensiones vía Consejo Minero, 🟡). Operativos de faena ~$930K–$2,25M (portales, 🟡) | Base ~$785.349/mes (CChC, 🟡) |
| **Costo de un mal trabajador** | **Catastrófico:** un incidente puede **paralizar la faena** (orden de US$ millones/día) y la mandante responde **solidariamente** (Art. 66 bis Ley 16.744 + DS 76, 🟢). Regulador sectorial (SERNAGEOMIN, DS 132) con poder de **multar y paralizar** | Alto pero acotado; sin regulador con poder de paralización equivalente |
| **Disposición a pagar** | Alta: la gran minería gastó **~US$23.000M en insumos/servicios (2023)** (Cochilco vía prensa, 🟡); proveedores APRIMIN facturan ~US$17.000M/año (🟢) | Sensible al precio; tickets menores |
| **Cultura de acreditación** | **Ya existe:** SICEP (~3.300–3.800 empresas acreditadas, exigido de facto por BHP, AMSA, SQM, Collahuasi, Teck, 🟢/🟡) → **menos cambio de hábito** | Más informal |
| **Nº de empresas (TAM)** | Menor: ~3.800 acreditadas SICEP / ~8.000 proveedores mineros (APRIMIN, 🟢) | Mucho mayor: ~88.675 empresas (🟡) |

**Lectura:** minería invierte el clásico trade-off — *menos* clientes potenciales pero cada uno con *mucho* mayor valor, presupuesto y predisposición a acreditar/pagar. Es el beachhead ideal; construcción es la expansión de volumen.

### 1-BIS.2 El matiz honesto sobre rotación (no se esconde)

Un dato podría parecer que *debilita* el caso minero, y hay que enfrentarlo de frente:
- Por sector, **minería rota 18,6% vs. construcción 50,0%** (INE, jun-2024, 🟢 — ambos confirmados leyendo el boletín). Menos rotación ⇒ a primera vista, menos decisiones de recontratación.

Por qué **no** debilita la tesis:
1. **Clasificación CIIU:** las contratistas de servicios mineros suelen quedar registradas como "Construcción" o "Servicios de apoyo", **no** como "Minería". El 18,6% refleja sobre todo a las **mandantes** (empleo estable), no a los **contratistas de faena**, cuya rotación real (contratos por obra) es mucho más alta. **No existe cifra INE que aísle al contratista minero.**
2. **El valor no es la rotación, es el riesgo** (ver Sección 1.3). La accidentabilidad minera es **baja en frecuencia** (1,0 vs 3,1 de construcción por 100 trabajadores, SUSESO 2023, 🟢) pero **altísima en severidad**: estallidos de roca, atrapamientos, fatalidades que **paralizan faenas completas** (ej. El Teniente, jul-2025: 6 fallecidos, SERNAGEOMIN paralizó la operación subterránea, 🟢). Ahí está el valor de filtrar trabajadores: no en evitar rotación, sino en **evitar el evento catastrófico**.

### 1-BIS.3 Corrección de dato heredado: % de contratistas

El material previo (`JUSTIFICACION_FAENASCORE.md`) cita "55-60% de la fuerza laboral minera es de contratistas". Ese dato es de **~2008** y está desactualizado. La cifra oficial reciente es **~75% (3 de cada 4)** en la gran minería (180.883 de 238.781 trabajadores; CCM-Eleva / Consejo Minero, estudios 2023-2032 y 2025-2034, 🟢). **La corrección agranda el segmento direccionable**, no lo reduce.

### 1-BIS.4 Implicación de pricing

Minería **soporta precio más alto** que el supuesto general: mayores sueldos (reemplazo más caro), contratos mayores y riesgo evitado de otra magnitud. Dos caminos posibles (a validar con WTP):
- **Opción A — mismo catálogo, posicionamiento premium:** vender los planes Empresa/Enterprise como la entrada natural del contratista minero (que casi siempre supera 100 trabajadores), sin tarifa distinta.
- **Opción B — tier "Minería" explícito:** un plan con add-ons que el rubro valora (integración con acreditación tipo SICEP, reportería para la mandante, trazabilidad de seguridad) a un precio por sobre Empresa. **Recomendado a mediano plazo**, una vez que los design partners mineros revelen WTP.

> **Conclusión 1-BIS:** anclar el *valor* y el *beachhead* en minería hace el caso más fuerte (mayor WTP, riesgo verificable, cultura de acreditación instalada) sin perder el TAM ancho de construcción para la expansión. Acción: los primeros design partners deben ser **contratistas mineros** (Faymex y su red), no construcción genérica.

---

## 2. Punto 2 — Evidencia de willingness-to-pay (WTP)

**Estado honesto: a hoy, CERO WTP revelada.** El precio se apoya en el juicio del fundador (*"en B2B industrial $30K vs $50K no cambia la decisión"*), que es una hipótesis razonable pero no un dato. Esto es lo correcto para una pre-seed, pero el inversor debe verlo declarado como hipótesis, no como hecho. Plan para convertirlo en evidencia:

### 2.1 WTP revelada (la más valiosa) — design partners
- Los **10 design partners** a precio fundador –50% de por vida son el primer instrumento de WTP **revelada** (no declarada). Métrica a capturar y reportar: de los contactados, **cuántos aceptaron al precio fundador sin regatear vs. cuántos negociaron**. El regateo marca el techo real de precio.
- Un "sí" con transferencia/factura emitida vale más que cualquier encuesta. La meta de los próximos 90 días es convertir 3–5 design partners en **ingreso real**, aunque sea descontado.

### 2.2 WTP declarada (complemento barato) — métodos estándar
- **Van Westendorp Price Sensitivity Meter** (P. van Westendorp, paper ESOMAR 1976, 🟢): 4 preguntas (demasiado caro / demasiado barato / empieza a ser caro / es una ganga) a 15–25 contratistas de la red de Germán → rango de precio aceptable y punto óptimo. Convierte "yo creo" en una curva.
- **Gabor-Granger** (Gabor & Granger, años 1960, 🟢): intención de compra a precios predefinidos ($39.990 / $49.990 / $69.990) → curva de demanda y precio que maximiza ingreso. Responde directamente "¿por qué $49.990 y no otro?".

### 2.3 Triangulación con gasto actual del cliente (proxy de WTP)
- Un contratista ya paga software de control de asistencia "por cabeza/mes". **No hay tarifa pública** (todos cotizan: GeoVictoria, Buk, Talana — 🔴), así que la afirmación "un cliente de 50 trabajadores ya gasta ~$75.000/mes en asistencia" es **estimación, no dato**. Única ancla numérica hallada: GeoVictoria España "desde 2 €/usuario/mes" (🟡, otro mercado). **Acción de DD:** pedir 3–4 cotizaciones reales con un headcount de 50 para fijar el benchmark de gasto del rubro.

> **Conclusión Punto 2:** método correcto y barato de ejecutar, pero **es el gap más importante**. Sin al menos 3 design partners pagando, el precio es una hipótesis bien argumentada. Prioridad #1.

---

## 3. Punto 3 — El value metric y el expansion revenue

### 3.1 Por qué "trabajadores activos" es el eje correcto (decisión argumentada)

| Eje candidato | Veredicto | Razón |
|---|---|---|
| Per-seat (supervisor) | ❌ | Subcaptura valor y **penaliza el comportamiento que genera el moat** (que muchos supervisores evalúen). |
| Per-worker exacto/mes | ⚠️ Base conceptual sí, factura no | Alinea con valor y con la convención chilena, pero fricción de conteo con rotación 50%. |
| Per-project | ❌ | Ingreso lumpy e impredecible. |
| **Flat por banda de trabajadores activos** | ✅ | Traduce el eje "trabajador" sin fricción; supervisores e histórico ilimitados. |

Esto es exactamente lo que un inversor quiere ver: el eje de cobro es una **elección defendida contra alternativas**, no un default copiado. Y está alineado con la convención que el cliente ya conoce: **todo el ecosistema chileno cobra por cabeza/mes** (Buk 🟢, Talana 🟢, GeoVictoria 🟢 — todos confirmados en su *modelo*, aunque no en su precio).

### 3.2 Expansion revenue / NRR — el argumento más fuerte y hoy implícito

El eje "trabajadores activos" es un **motor de expansión automática**: cuando el cliente gana más obras y mueve más gente, sube de banda solo, sin re-negociación. Esto debería cuantificarse como driver de **Net Revenue Retention**:
- Benchmark: NRR mediana SaaS privado ~**101%** (Benchmarkit 2024, 🟢); >100% es bueno, 120%+ es best-in-class (marco Bessemer, 🟢). En segmento SMB la mediana es ~**97%** (ChartMogul, 🟢), así que **mantener ~100% NRR en SMB ya es sólido**; no hay que prometer 120%.
- El **histórico ilimitado gratis** es deliberado: el dato acumulado es el switching cost. Cobrarlo desincentivaría acumularlo. Se cobra por **capacidad operativa actual** (trabajadores activos), no por el acervo histórico → el moat crece gratis mientras el ingreso escala con el uso.

> **Conclusión Punto 3:** el punto más fuerte del estudio. Acción: convertir "expansion natural" en una proyección de NRR con cohortes (aunque sean sintéticas al inicio).

---

## 4. Punto 4 — Benchmarking competitivo (verificado y señalizado)

### 4.1 Chile — el eje dominante es "por colaborador/mes", y NADIE publica precio

| Producto | Categoría | Modelo de cobro | Precio público | Confianza |
|---|---|---|---|---|
| **Buk** | Suite RRHH oficina | Por colaborador/mes, desc. por volumen; desempeño = módulo aparte | No (ref. GetApp ~US$95/mes) | Modelo 🟢 / precio 🔴 |
| **Talana** | Suite RRHH + asistencia | Por trabajador activo/mes, modular | No (ref. mercado 1–3 UF) | Modelo 🟢 / precio 🟡 |
| **Rankmi** | Desempeño/personas | Suscripción por empleados + módulos | No | 🔴 |
| **Nubox** | Contab.+remun. PYME | Planes/paquetes | $15.000–$49.900/mes (comparador) | 🟡 |
| **Defontana** | ERP modular (Zenda) | Cotización | No | 🔴 |
| **GeoVictoria** | Asistencia terreno | Por usuario activo/mes (fijo ≤10, variable ≥11) +IVA | No (Chile); España "desde 2€/usuario/mes" | Modelo 🟢 / precio 🔴 (Chile) |

**Hallazgo crítico para el inversor:** el rumor interno de "GeoVictoria ~$1.000–2.500 CLP/trabajador/mes" **NO se pudo confirmar en ninguna fuente chilena** (🔴). La única ancla numérica es GeoVictoria España (~2 €/usuario ≈ ~$2.000 CLP, 🟡), coherente con el rango pero de otro mercado. **Cualquier comparación de precio con GeoVictoria en un pitch debe marcarse como estimación sujeta a cotización.** Distinguir esto es lo que separa un benchmarking serio de uno inventado.

### 4.2 Global — referencias de performance/workforce SaaS (sí publican)

| Producto | País | Modelo | Precio (USD) | Confianza |
|---|---|---|---|---|
| **Workyard** | USA | Base fee + per-user | **$50/mes base** + $8 (Starter) / $16 (Pro) por usuario; $6 anual; trial 14 días | 🟢 |
| **Connecteam** | Israel | Flat primeros 30 users; free ≤10 | Basic ~$29/mes anual; trial 14 días | 🟢 |
| **BambooHR** | USA | Per-employee; performance = add-on | ~$10/$17/$25 PEPM; mín. ~$250/mes | 🟡 (oficial bloqueado) |
| **Lattice** | USA | Per-seat; performance = **core** | **$8/seat/mes** (Performance); mín. anual $4.000 | 🟢 |
| **15Five** | USA | Per-user | Engage $4 / Perform $11 / Total $16 por user/mes | 🟢 |
| **Rhumbix / Riskcast / Arcoro** | USA | Enterprise, per-user/per-project | Sin precio público (Arcoro ~$5–15 PEPM estimado) | 🔴/🟡 |
| **Procore** | USA | % del volumen de obra (ACV) | Sin precio público (~$15K–80K/año estimado) | Modelo 🟢 / precio 🟡 |

**Dos aprendizajes que el pricing de Recontrata ya incorpora (bien):**
1. El **base fee fijo de Workyard ($50/mes) es criticado** por empresas chicas con fuerza laboral fluctuante — exactamente el perfil de Recontrata (rotación 50%). Por eso **no copia el base fee**: usa flat por banda, más amable. Decisión correcta y ahora respaldada con dato verificado.
2. **Performance casi siempre es add-on** (BambooHR 🟡) o producto per-seat aparte (Lattice $8 🟢, 15Five Perform $11 🟢). Recontrata, al ser un producto *enfocado* en desempeño de terreno y cobrar por trabajador (no por seat), se posiciona distinto y evita el "módulo escondido en una suite cara".

### 4.3 Lectura de posicionamiento de precio
Recontrata Pro a $49.990/mes (~US$53 al tipo de cambio ~$950/USD, ⚙️ supuesto) por **hasta 100 trabajadores con supervisores ilimitados** equivale a **~US$0,53 por trabajador/mes** — un orden de magnitud **por debajo** de los per-user globales ($8–16 de Workyard/Lattice) y por debajo del rango estimado de asistencia local. Esto sustenta el argumento de **headroom de precio**: hay espacio para subir sin salirse del mercado.

> **Conclusión Punto 4:** benchmarking honesto y bien señalizado. Su mayor virtud es declarar qué precio NO pudo confirmar. Acción de DD: cotizaciones reales de GeoVictoria/Buk/Talana para fijar el ancla local.

---

## 5. (Reservado — el Punto 5 son los unit economics, Sección 6)

---

## 6. Punto 5 — Unit economics (modelo con supuestos marcados)

⚠️ **Advertencia de honestidad:** sin clientes pagando, todo aquí es **proyección con supuestos explícitos**, no medición. Un inversor de pre-seed espera el *marco* y la *sensibilidad*, no cifras reales. Los supuestos están marcados ⚙️ para que se puedan cuestionar uno por uno.

**Supuestos base (editables):**
- ARPA plan Pro: $599.880 CLP/año (🟢 derivado del precio decidido).
- Margen bruto: **82%** ⚙️ (infra Railway/Supabase/OpenAI es barata; resta soporte + onboarding asistido). Benchmark SaaS sano: 75–85%.
- Churn anual SMB temprano: **20%** ⚙️ → vida media 5 años. (SMB churnea más que enterprise; 20% es prudente).
- CAC venta consultiva 1:1 founder-led: **$400.000 CLP** ⚙️ (costo de tiempo de venta + demo + onboarding; sin paid ads aún).

**Resultados ⚙️ DERIVADOS:**
| Métrica | Cálculo | Resultado | Benchmark |
|---|---|---|---|
| LTV | $599.880 × 0,82 ÷ 0,20 | **~$2,46M CLP** | — |
| LTV : CAC | $2,46M ÷ $400K | **~6,1 : 1** | >3:1 sano (D. Skok, 🟢) |
| Payback de CAC | $400K ÷ ($49.990 × 0,82) | **~9,8 meses** | <12 meses (D. Skok, 🟢) |
| Margen bruto | — | 82% | 75–85% sano |

**Matiz del benchmark de payback:** la regla "<12 meses" es de David Skok (For Entrepreneurs, 🟢) y data de ~2011 (capital escaso); el propio Skok reconoce que hoy es raro y que enterprise con land-and-expand opera sano a ~20 meses. Para SMB venta consultiva, <12 meses sigue siendo excelente. Si el CAC real sube a $600K, el payback va a ~15 meses y LTV:CAC a ~4:1 — **aún saludable** (ver sensibilidad en 7.2).

> **Conclusión Punto 5:** los unit economics *cierran cómodamente* incluso con supuestos prudentes, y aguantan que el CAC se duplique. La debilidad es que son proyección. Acción: instrumentar CAC y churn reales desde el primer design partner pagado.

---

## 7. Punto 6 — Sensibilidad y escenarios

### 7.1 Conversión y ramp (con benchmarks verificados)
- **Trial → pago (con tarjeta):** bueno 25–35%, grande 50–60%; **sin tarjeta** bueno 4–6% (ChartMogul, ene-2026, 🟢). Trial de **14 días** es la duración dominante (62% de productos, 🟢).
- **Freemium → pago:** promedio **~3,7%** (rango 2,6–6,1% por industria; First Page Sage, jun-2026, 🟢); 2–5% (OpenView 2022, 🟢).
- **Modelo híbrido freemium+trial:** OpenView confirma que las PLG exitosas combinan ambos (🟢, cualitativo). El "**65% lo usa**" es 🔴 **NO VERIFICABLE** — no citarlo como dato.
- **Activación = predictor clave:** usuarios que activan en la 1ª semana retienen 3–5× más a 30 días (Mixpanel vía Appcues, 🟡). Ojo: ese 3–5× es de **retención**, no "conversión vs. precio" — esa formulación es 🔴 NO VERIFICABLE. El matiz propio de Recontrata sigue válido: el "momento ajá" (armar la 2ª cuadrilla filtrando por score) tarda **más de 14 días**, por eso el freemium (deja madurar el dato) + trial (para el que ya tiene varias faenas).

### 7.2 Escenarios de ARR (ilustrativos, ⚙️ DERIVADOS)
Supuesto: 500 contratistas en el funnel anual (free + trials). Mix 100% plan Pro para simplificar; ARPA $599.880/año.

| Escenario | Conversión a pago | Clientes pago | ARR | Lectura |
|---|---|---|---|---|
| Pesimista | 3% (freemium puro) | 15 | ~$9,0M CLP | Ramp lento; necesita más funnel |
| Base | 6% (híbrido) | 30 | ~$18,0M CLP | Coherente con SOM año 1–2 del doc (~US$100–200K) |
| Optimista | 12% (trial con tarjeta bien activado) | 60 | ~$36,0M CLP | Requiere activación fuerte + tarjeta en trial |

⚙️ Nota: el SOM del doc interno (~US$100–200K/año = ~$95–190M CLP) **no concilia** con estos números a 500 contratistas; implica >300 clientes pagados, lo que exige un funnel mucho mayor o ARPA mixto con planes Empresa/Enterprise. **Acción:** rehacer el TAM/SAM/SOM bottom-up (Sección 9) para que el SOM sea defendible.

### 7.3 Sensibilidad al precio
- A elasticidad desconocida (aún sin Van Westendorp), el rango a testear es **$39.990 / $49.990 / $69.990**. El argumento "B2B industrial no es sensible bajo el umbral gerencial (~$150K)" es plausible pero **no medido**. La sensibilidad real saldrá de Gabor-Granger (Sección 2.2).

> **Conclusión Punto 6:** el estudio modela la incertidumbre en vez de dar un número único — bien. Acción: cerrar la inconsistencia del SOM y reemplazar supuestos de conversión por datos al tener trials reales.

---

## 8. Punto 7 — Coherencia entre el estudio de precios y el producto

Aquí están los dos hechos que **un inversor descubriría en due diligence** y que el estudio declara por adelantado (la honestidad protege la credibilidad del resto):

### 8.1 El producto todavía no puede cobrar (gap de ejecución, no de tesis)
- QA de lanzamiento (26-jun-2026): la monetización **no existe**. Los planes de la landing son **vitrina**: no hay integración de pagos (Webpay/MercadoPago/Stripe) ni **enforcement** de límites (el "Gratis 15 trabajadores" no se aplica; hoy se carga ilimitado). Es normal en pre-lanzamiento, pero el pricing no es "real" hasta que exista billing + límites + transferencia/factura (medio de pago crítico en B2B chileno).

### 8.2 Riesgo legal que toca el corazón del pricing y el moat 🔴 (el más importante)
- El moat y la justificación de los planes superiores (Empresa/Enterprise multi-empresa, "insights", API) descansan en el **dato histórico acumulado y compartido**. Pero:
  - La DT declara **ILEGAL** usar datos de la relación laboral para construir **registros o listas negras** que impidan la contratación en otras empresas (**ORD N°1782/30, 10-abr-2015, 🟢 oficial**). Fundamento: art. 19 N°16 Constitución, arts. 5° y 154 bis Código del Trabajo, Ley 19.628.
  - Entra en vigencia plena en **diciembre 2026 la Ley 21.719** de protección de datos personales (🟢), que endurece el tratamiento.
- **Implicancia de pricing:** una evaluación de desempeño es legítima **dentro de cada empleador**; un registro **compartido entre empresas** para vetar contrataciones cae en la prohibición. El producto debe mantener los datos **bajo control del empleador titular** y no exponer evaluaciones a terceros sin consentimiento del trabajador. Esto **acota qué puede venderse en los planes superiores** (no se puede monetizar un "buró de trabajadores" inter-empresa). El plan Enterprise debe diseñarse como multi-faena *dentro de un mismo holding/empleador*, no como red de reputación compartida. Recontrata ya tiene el ángulo correcto ("reemplazo legal de listas negras, vía Reglamento Interno"), pero el inversor debe ver que el límite legal está **internalizado en el diseño de los planes**, no como nota al pie.

> **Conclusión Punto 7:** el estudio gana credibilidad al declarar estos dos puntos. El legal no es un "riesgo menor": define la frontera de lo monetizable. Acción: validación legal del modelo de datos antes de construir el plan Enterprise.

---

## 9. TAM / SAM / SOM (bottom-up, a reconstruir con rigor)

El dimensionamiento del doc interno (TAM ~US$3–18M, SAM ~US$2–3M, SOM ~US$100–200K) es un rango demasiado ancho para un inversor. Bottom-up con datos verificados:

Por coherencia con el sector ancla, se dimensiona en **dos capas**: minería (beachhead) y construcción (expansión).

**Capa 1 — Beachhead minero (entrar aquí):**
- **Universo:** ~**8.000 proveedores** de la minería (APRIMIN, 🟢), de los cuales ~**3.800 están acreditados en SICEP** (subconjunto de mayor WTP, ya acostumbrado a calificar, 🟢/🟡).
- **Trabajadores:** gran minería ~**200.000** en faena, **~75% vía contratistas** = ~150.000 trabajadores de contratistas gestionables (CCM-Eleva/Consejo Minero, 🟢).
- ⚙️ **DERIVADO:** tomando las ~3.800 empresas SICEP como SAM cualificado, a un ARPA premium minero de ~**$1,2M/año** (plan Empresa, contratistas que casi siempre superan 100 trabajadores) → **SAM minero ≈ $4.560M CLP/año (~US$4,8M)**. SOM de captura 2–3% año 1–2 = **~$90–140M CLP (~US$95–145K)**.

**Capa 2 — Expansión construcción (volumen):**
- **Universo:** ~**88.675 empresas** activas en construcción (SII vía agregador, 🟡; desglose por tamaño en un .xlsx oficial del SII a descargar). **712 mil ocupados** (CChC/INE, 🟢) + **1.071.128 subcontratados** país (INE 2024).
- ⚙️ **DERIVADO:** SAM de contratistas medianos (20–200 trab.), ~8.000 empresas estimadas, ARPA mixto ~$700K/año → **SAM ≈ $5.600M CLP/año (~US$5,9M)**.

**TAM combinado (minería + construcción + servicios industriales):** orden de **~US$10–11M/año** de SAM, con expansión LATAM (Perú, Colombia, México: misma industria, mismo dolor) como multiplicador.

> **Conclusión Sección 9:** el doble dimensionamiento concilia con el SOM histórico (~US$100–200K año 1–2) y, lo más importante, **define por dónde entrar**: las ~3.800 empresas SICEP son una lista direccionable y finita, no un "mercado" abstracto. Acciones concretas: (1) descargar el .xlsx del SII (construcción por tamaño); (2) revisar el Barómetro SICEP 2025 para el desglose de proveedores mineros por tamaño/región.

---

## 10. Riesgos del pricing (resumen para DD)

| Riesgo | Severidad | Estado |
|---|---|---|
| WTP no validada (precio = juicio del fundador) | 🔴 Alta | Plan en Sección 2; sin ejecutar |
| Producto no puede cobrar (sin billing/límites) | 🟠 Media | Verificado en QA; es trabajo de ingeniería |
| Límite legal al dato compartido (listas negras / Ley 21.719) | 🔴 Alta | Acota planes superiores; requiere validación legal |
| Benchmark de competidores con precios no confirmados | 🟡 Media | Mitigar con cotizaciones reales |
| SOM inconsistente con conversión × funnel | 🟢 Baja | Reconciliado con bottom-up doble capa (Sección 9); refinar con .xlsx SII + Barómetro SICEP |
| Unit economics proyectados, no medidos | 🟡 Media | Se resuelve con primeros clientes |
| Costo-de-reemplazo mal anclado (50% sin fuente) | 🟢 Baja | Corregido a 16–20% (CAP) y reencuadrado a riesgo minero (Sección 1) — mejora el caso |
| Rotación minera baja (18,6%) podría leerse como menor mercado | 🟡 Media | Aclarado: el contratista de faena no está en el CIIU minería; el valor es riesgo, no rotación (Sección 1-BIS.2) |

---

## 11. Tabla maestra de fuentes (para verificación posterior)

> Todas consultadas 27–28 jun 2026. Re-confirmar precios antes de uso externo.

**Mercado y normativa Chile — construcción**
- INE — Tasa de Rotación Laboral jun-2024 (construcción 50,0%; **minería 18,6%**; nacional 30,0%) 🟢 [boletín N°6, tabla por actividad] — https://www.ine.gob.cl/docs/default-source/estadisticas-registros-administrativos/boletines/tasas-de-rotaci%C3%B3n-laboral/2024/junio-2024.pdf
- CChC/INE — Empleo construcción 712 mil ocupados (ago-2025) 🟢 — https://cchc.cl/documents/431409/539255/Empleo_Imacon_agosto2025+-+Orlando+Robles.pdf
- CChC — Índice Remuneraciones construcción ~$785.349 (mar-2024) 🟡 — https://cchc.cl/documents/431409/539255/2024-04-Indice-Remuneraciones-Abril.pdf
- INE — Ingreso laboral mediano $611.162 / promedio $897.019 (2024) 🟢 — https://www.ine.gob.cl/sala-de-prensa/prensa/general/noticia/2025/08/11/
- SII — Estadísticas de empresas por rubro y tramo (descargar .xlsx) 🟢 — https://www.sii.cl/sobre_el_sii/estadisticas_de_empresas.html
- Empresas construcción ~88.675 (agregador SII) 🟡 — https://chilerutempresa.cl/estadisticas
- DT — ORD N°1782/30 (listas negras ilegales, 10-abr-2015) 🟢 — https://www.dt.gob.cl/legislacion/1624/w3-article-105416.html
- DT/BCN — Ley 20.123 subcontratación y acreditación (art. 183-C) 🟢 — https://www.dt.gob.cl/portal/1626/w3-article-93827.html
- DT — Resolución Exenta N°38 (sistemas de control de asistencia, 26-04-2024) 🟢 — https://www.dt.gob.cl/portal/1626/w3-article-124477.html
- **Center for American Progress** (think tank de políticas públicas de EE.UU.) — Boushey & Glynn (2012), *"There Are Significant Business Costs to Replacing Employees"*; costo de reemplazo ~20% salario (16% para <$30k) 🟢 [fuente primaria del criterio] — artículo: https://www.americanprogress.org/article/there-are-significant-business-costs-to-replacing-employees/ · PDF: https://www.americanprogress.org/wp-content/uploads/sites/2/2012/11/CostofTurnover.pdf
- Gallup — McFeely & Wigert (2019), costo de reemplazo "½ a 2× salario" (50–200%) 🟢 — https://www.gallup.com/workplace/247391/fixable-problem-costs-businesses-trillion.aspx
- Work Institute — Retention Report 2017, costo 33% salario (vía HR Dive) 🟡 — https://www.hrdive.com/news/study-turnover-costs-employers-15000-per-worker/449142/

**Sector minero Chile (ancla/beachhead)**
- Consejo Minero / CCM-Eleva — Estudio Fuerza Laboral Gran Minería: ~75% contratistas (180.883 de 238.781) 🟢 — https://ccm-eleva.cl/wp-content/uploads/2023/12/EstudioFuerzaLaboral2023_2032.pdf
- Consejo Minero — Reporte Anual 2025: ~305.000 empleo directo (máximo en 15 años) 🟢 — https://consejominero.cl/prensa/consejo-minero-releva-el-rol-estrategico-de-la-mineria-en-su-reporte-anual-2025/
- Sup. de Pensiones vía Consejo Minero (La Tercera/Pulso) — minería = sector mejor pagado, imponible ~$2,31M 🟡 — https://www.latercera.com/pulso/noticia/cuanto-ganan-los-trabajadores-mineros-esforzados-yo-privilegiados/G6M7XHL5I5HZZKLQ7Z3VG6MGSI/
- APRIMIN — ~8.000 proveedores de la minería; socios facturan ~US$17.000M/año 🟢 — https://aprimin.cl/site/corporativas/varian-en-numero-de-colaboradores-tamano-de-empresa-y-nivel-de-facturacion-chile-cuenta-con-al-menos-ocho-mil-proveedores-de-la-mineria/
- SICEP — ~3.300–3.800 empresas acreditadas; 27 mandantes usuarios (BHP, AMSA, SQM, Teck, Collahuasi) 🟢/🟡 — https://www.sicep.cl/ · https://www.portalminero.com/wp/proveedores-y-companias-mineras-se-reunieron-en-encuentro-sicep-aia-santiago-2025/
- Cochilco (vía prensa) — gasto gran minería en insumos ~US$23.147M (2023) 🟡 — https://editorialrn.com.ar/gran-mineria-chilena-gasta-us23-mil-millones-gestion-legal-en-contratos-emerge-como-optimization-pendiente/
- SERNAGEOMIN — Reglamento de Seguridad Minera DS 132 (multas 20–50 UTM, facultad de paralización) 🟢 — https://www.bcn.cl/leychile/Navegar?idNorma=221064
- SERNAGEOMIN — paralización El Teniente (jul-2025, 6 fallecidos) 🟢 — https://www.codelco.com/prensa/2025/sernageomin-autoriza-reinicio-parcial-y-progresivo-de-operaciones
- SUSESO — Informe Anual 2023: accidentabilidad minería 1,0 vs construcción 3,1 (por 100 trab.) 🟢 — https://www.suseso.cl/605/w3-article-729381.html
- Mandante responde solidariamente por seguridad del contratista (Art. 66 bis Ley 16.744 + DS 76) 🟢 — https://www.bcn.cl/leychile/Navegar?idNorma=221064
- SHRM — costo de reemplazo "50–200% / 6–9 meses" 🔴 NO VERIFICABLE (sin fuente primaria; solo blogs) — https://waterfallplanning.com/learn/the-real-cost-of-employee-turnover/

**Competidores Chile**
- Buk precios (modelo por colaborador) 🟢 modelo — https://www.buk.cl/precios
- Talana cotización 🟢 modelo — https://web.talana.com/cotiza
- Rankmi desempeño 🔴 precio — https://www.rankmi.com/es/productos/desempeno-y-competencias
- Nubox (comparador guiadesoftware) 🟡 — https://www.guiadesoftware.com/software/nubox
- GeoVictoria (modelo por usuario activo) 🟢 modelo / 🔴 precio Chile — https://www.comparasoftware.cl/geovictoria · https://info.geovictoria.com/es-es/precios

**Competidores globales**
- Workyard pricing ($50 base + $8/$16 user, trial 14d) 🟢 — https://www.workyard.com/pricing
- Connecteam pricing (free ≤10, flat 30 users) 🟢 — https://connecteam.com/pricing/
- Lattice pricing (Performance $8/seat) 🟢 — https://lattice.com/pricing
- 15Five pricing (Engage $4 / Perform $11 / Total $16) 🟢 — https://www.15five.com/pricing
- BambooHR pricing (PEPM, performance add-on) 🟡 — https://peoplemanagingpeople.com/tools/bamboohr-pricing/
- Procore pricing (% de ACV) 🟢 modelo — https://www.procore.com/pricing
- Arcoro / Rhumbix / Riskcast 🟡/🔴 — https://arcoro.com/pricing · https://www.rhumbix.com/pricing · https://riskcast.com/

**Benchmarks de pricing SaaS**
- ChartMogul SaaS Conversion Report (ene-2026): trial 25–35% c/tarjeta, 14 días 62% 🟢 — https://chartmogul.com/reports/saas-conversion-report/
- First Page Sage: freemium ~3,7% (jun-2026) 🟢 — https://firstpagesage.com/seo-blog/saas-freemium-conversion-rates/
- OpenView Product Benchmarks 2022 (trial 17% / freemium 5%) 🟢 — https://openviewpartners.com/2022-product-benchmarks/
- David Skok / For Entrepreneurs: LTV:CAC >3, payback <12m 🟢 — https://www.forentrepreneurs.com/saas-metrics-2-definitions-2/
- Benchmarkit 2024: NRR mediana ~101% 🟢 — https://www.benchmarkit.ai/2024benchmarks
- ChartMogul: NRR por segmento (SMB ~97%) 🟢 — https://chartmogul.com/reports/saas-retention-the-new-normal/
- LeveragePoint: % de captura de valor es contextual 🟢 — https://www.leveragepoint.com/blog/pricing/what-percent-of-value-should-we-capture-in-price/
- Van Westendorp PSM (ESOMAR 1976) 🟢 — https://en.wikipedia.org/wiki/Van_Westendorp's_Price_Sensitivity_Meter
- Gabor-Granger (descripción) 🟢 — https://www.surveymonkey.com/market-research/resources/gabor-granger-vs-van-westendorp/
- Activación 3–5× retención (Mixpanel vía Appcues) 🟡 — https://www.appcues.com/blog/product-activation-metric

**Cifras descartadas por no verificables (🔴 — no citar como duras):** "65% PLG usa híbrido"; "captura 10–25% del valor" como benchmark medido; "activación predice conversión 3–5× sobre el precio"; GeoVictoria "$1.000–2.500 CLP/trabajador" (Chile).

---

## 12. Veredicto del inversor

**¿El pricing de Recontrata estuvo bien hecho?** Sí en *método*, parcialmente en *evidencia*.

✅ **Lo que convence:**
- Precio derivado del valor, con un eje de cobro elegido contra alternativas y alineado a la convención del mercado.
- **Sector ancla bien elegido:** minería como beachhead (mayor WTP, riesgo de otra magnitud, cultura de acreditación SICEP ya instalada) + construcción como TAM de volumen.
- Expansion revenue estructural por diseño (cobra por trabajadores, no por seat; histórico gratis).
- Benchmarking honesto que distingue lo confirmado de lo estimado.
- Unit economics que cierran con holgura incluso bajo supuestos prudentes.
- El dolor está cuantificado con fuentes oficiales (rotación construcción 50% / minería 18,6% INE; ~75% de la gran minería es contratista; ~305 mil empleo directo).
- **El estudio se autocorrige con honestidad:** desechó el "50% del salario" mal fundado (→ 16–20% CAP), descartó 3 cifras "de pasillo" no verificables, y corrigió el "55-60% de contratistas" (→ ~75%). Eso señala un equipo que sabrá ajustar el precio cuando lleguen los datos.

⚠️ **Lo que exijo antes de invertir con convicción (en orden):**
1. **3–5 design partners *mineros* pagando** → WTP revelada en el beachhead correcto (hoy es el gap #1).
2. **Validación legal del modelo de datos** (listas negras / Ley 21.719) → define qué se puede vender en planes superiores.
3. **Billing + enforcement de límites** funcionando → el pricing deja de ser vitrina.
4. Refinar el SAM con el **.xlsx del SII** (construcción por tamaño) y el **Barómetro SICEP** (proveedores mineros por tamaño).
5. Reemplazar supuestos de unit economics por **CAC y churn medidos** con los primeros clientes; evaluar un **tier "Minería" premium** una vez revelada la WTP.

**En una frase:** es un estudio de pricing de calidad por encima del promedio para una pre-seed —piensa en value metric, sector ancla, expansión y honestidad de fuentes— pero su número final aún se apoya en juicio, no en datos. Resolver los 5 puntos de arriba en los próximos 90 días, **entrando por minería**, lo convierte de "tesis bien argumentada" en "tesis probada".

---

*Documento elaborado el 28 de junio de 2026. Fuentes verificadas 27–28 jun 2026; re-confirmar precios de terceros antes de uso comercial o de levantamiento de capital.*
