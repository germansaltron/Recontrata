# FaenaScore — Informe de Justificacion de Proyecto

> Sistema de inteligencia de fuerza laboral para contratistas industriales.
> Autor: German / Faymex | Fecha: 11 de abril 2026

---

## 1. Origen del proyecto

FaenaScore nace de una investigacion exhaustiva de 12 oportunidades micro-SaaS con IA (documento "Investigacion Micro-SaaS IA Abril 2026") donde se evaluaron ideas para automatizar tareas tediosas usando IA actual.

La idea original #6 del documento, **EvalPro** (generador de evaluaciones de desempeno para PYMEs), fue re-investigada y **pivoteada radicalmente** al detectar que:

1. El EvalPro original apuntaba a gerentes de oficina — mercado ya cubierto por Buk, Talana y Factorial.
2. El dolor REAL identificado por German (fundador de Faymex, empresa contratista industrial) es completamente diferente: **no hay datos estructurados para decidir a quien recontratar en faenas industriales**.
3. Este dolor especifico no tiene solucion en Chile ni en LATAM.

---

## 2. El problema

### 2.1 Contexto: Trabajadores temporales en Chile

- **1,071,128 trabajadores subcontratados** en Chile (INE 2024, 15.5% de asalariados).
- **~75% de la fuerza laboral de la gran minería** es de empresas contratistas (Consejo Minero / CCM-Eleva, estudios 2023-2032 y 2025-2034: 180.883 de 238.781 trabajadores). *Corrige el dato previo de "55-60%", que era de ~2008.*
- El **contrato por obra o faena** (Art. 10 bis, Codigo del Trabajo) es el mecanismo estandar: el trabajador se vincula a un proyecto especifico y al terminar, la relacion laboral termina.
- La construccion tiene **50% de rotacion laboral** — la mas alta de todos los sectores en Chile.

### 2.2 Como se toman decisiones de recontratacion HOY

Cuando un contratista gana un nuevo proyecto y necesita armar una cuadrilla (ej: "20 soldadores 4G para Chuquicamata en 3 semanas"), el proceso actual es:

1. **Memoria del jefe de obra**: "Me acuerdo que el Mario era bueno".
2. **WhatsApp**: la "base de datos" es la agenda de contactos del capataz.
3. **Boca a boca**: recomendaciones informales entre supervisores.
4. **Listas negras ilegales**: la Federacion Minera ha denunciado planillas con 2,854+ nombres vetados. La DT las declara inconstitucionales, pero existen porque no hay alternativa legal estructurada.
5. **Excel basico**: si acaso, una planilla con nombre, RUT y telefono.

**Lo que NO se captura:**
- Rendimiento en proyectos anteriores
- Tasa de ausentismo por trabajador
- Incidentes de seguridad individuales
- Feedback de diferentes supervisores
- Razon de no-recontratacion
- Tendencia de desempeno en el tiempo

**La informacion muere con cada proyecto.** Cuando termina un contrato de 6 meses, los supervisores se van a otra faena, los trabajadores se dispersan, y nadie registra quien fue bueno y quien no.

### 2.3 El costo de no tener datos

- Reemplazar un trabajador operativo cuesta **~16-20% de su sueldo anual** (~$1,5M CLP, sobre un sueldo base de construccion de ~$785.349/mes). *Reemplaza la cifra previa de "50% (~$750K)", que no tenia fuente y estaba mal anclada.*
  - **Fuente del criterio:** Center for American Progress (CAP), instituto de investigacion de politicas publicas de EE.UU. Estudio de Heather Boushey y Sarah Jane Glynn, *"There Are Significant Business Costs to Replacing Employees"* (16-nov-2012), meta-analisis de 30 case studies en 11 papers (1992-2007). Hallazgo: costo de rotacion ≈20% del salario anual tipico, **16% para sueldos bajos (<US$30k/ano)**, hasta 213% en ejecutivos. Consultable en: https://www.americanprogress.org/article/there-are-significant-business-costs-to-replacing-employees/ (PDF: https://www.americanprogress.org/wp-content/uploads/sites/2/2012/11/CostofTurnover.pdf).
- A modo de magnitud, un contratista con 200 trabajadores y 40% de rotacion enfrenta ~80 reemplazos/ano; el costo total de rotacion ronda los **~$120 millones CLP/ano**. Recontrata no evita la rotacion estructural (los contratos por obra terminan por diseno): reduce el subconjunto de **malas recontrataciones** y el riesgo asociado.
- Recontratar a un mal trabajador implica: re-trabajo, incidentes de seguridad, baja productividad, y potencial perdida de contrato con la minera mandante. **En faena minera ese riesgo es de otra magnitud** (paralizacion de faena, responsabilidad solidaria de la mandante); ver `ESTUDIO_PRECIOS_INVERSOR.md`.

---

## 3. Investigacion de mercado

### 3.1 Lo que YA existe vs. lo que FALTA

| Categoria | Herramientas existentes | Que resuelven | Que NO resuelven |
|---|---|---|---|
| Acreditacion | SIGA, Validate, Workmate | "Puede entrar a la faena?" | "Deberia VOLVER a la faena?" |
| Certificaciones | ChileValora, AWS | Competencia tecnica minima | Desempeno real en proyecto |
| Asistencia | GeoVictoria, IConstruye Builder | Horas trabajadas, asistencia | Calidad del trabajo |
| Compliance | Validate, Certilap | Cumplimiento Ley 20.123 | Evaluacion individual |
| RRHH oficina | Buk, Talana, Factorial | Eval 360 para empleados fijos | Trabajadores temporales de terreno |
| KPIs contrato | Sistemas de la minera mandante | Desempeno de la empresa contratista | Desempeno del trabajador individual |

**El gap esta entre "puede entrar a la faena" (acreditacion) y "deberia volver a la faena" (desempeno). Nadie lo cubre.**

### 3.2 Competencia directa: Practicamente cero

| Herramienta | Pais | Evaluacion blue-collar? | En Chile/LATAM? |
|---|---|---|---|
| Buk / Talana | Chile | Si, pero para oficina | Si, pero no para faena |
| GeoVictoria | Chile | NO — solo asistencia | Si |
| IConstruye | Chile | NO — supply chain | Si |
| Validate | Chile | NO — solo compliance | Si |
| MyPass Global | Australia | Parcial — credenciales | NO |
| Procore Workforce | USA | Lo mas cercano | NO opera en LATAM |
| Connecteam | Israel | Parcial — formularios | NO enfocado en recontratacion |
| Arcoro | USA | Limitado, solo ingles | NO |

**No existe en Chile ni en LATAM una herramienta disenada para evaluar trabajadores temporales de faena con el fin de informar decisiones de recontratacion.**

### 3.3 Marco legal chileno

- El Codigo del Trabajo **no obliga** evaluaciones de desempeno, pero la DT permite implementarlas si se incluyen en el Reglamento Interno (Ord. N 3406/50).
- Las **listas negras son ilegales** (contrarias a la Constitucion y ley laboral). FaenaScore las reemplaza con un sistema legal, transparente y estructurado.
- El mal desempeno **no es causal directa de despido** (Art. 161 es para necesidades de la empresa). Pero la documentacion SI sirve para Art. 160 N7 (incumplimiento grave) y, mas importante, para la decision de **no recontratar** — que es el caso de uso principal.
- **ChileValora** (Ley 20.267) provee perfiles de competencias por oficio que pueden usarse como baseline de evaluacion.

---

## 4. Ideas descartadas y por que

Durante la investigacion se evaluaron las 12 ideas del documento original. Las siguientes fueron descartadas tras validacion con la realidad del mercado chileno:

| Idea | Score original | Score real Chile | Razon de descarte |
|---|---|---|---|
| **RecibosAI** | 9.0 | 5.0 | Boleta electronica obligatoria desde 2021. El SII ya tiene toda la data en XML. Nubox, Defontana, SyncManager ya resuelven esto. |
| **FotoListo** | 8.5 | 3.0 | MercadoLibre ya ofrece gratis: fotos IA, titulos sugeridos, descripciones automaticas, Mercado Clips. Riesgo de plataforma critico. |
| **ContractSnap** | 8.0 | 4.0 | 7+ competidores chilenos activos: Magnar AI (5,000 usuarios, inversion de Carey), Cicero.cl ($280/mes), Spektr (alianza PUC). Mercado saturado. |
| **ExtractaBank** | 8.0 | 3.0 | Open Banking (Ley 21.521) entra en vigencia julio 2026. Fintoc ya conecta 5 bancos principales. CartolaSimple.cl hace OCR gratis. Timing pesimo. |
| **CalificaRapido** | 8.5 | 6.5 | Gap real en espanol, pero: OCR manuscrito con 7.66% error, 70% padres rechazan IA calificando, profesores ganan $640K/mes (baja disposicion a pagar). Riesgoso. |
| **EvalPro** (original) | 8.0 | 6.0 | Version oficina ya resuelta por Buk/Talana. Pivoteado a FaenaScore (version industrial). |

### Ideas con potencial que se mantienen en pipeline

| Idea | Score real | Estado |
|---|---|---|
| **LicitaDoc** | 8.5 | Evaluada positivamente. Nadie genera propuestas tecnicas con IA en Chile. LicitaLAB valido el mercado (1,000 clientes). |
| **AcreditaMinero** | 8.0 | Complementaria a FaenaScore. Gestion de documentos de acreditacion para contratistas. |

---

## 5. La solucion: FaenaScore

### 5.1 Que es

Un sistema mobile-first de evaluacion de desempeno para trabajadores temporales de faena, disenado para contratistas de mineria, construccion y servicios industriales.

**Proposito central**: Transformar la memoria personal y los WhatsApp del capataz en datos estructurados que permitan tomar mejores decisiones de recontratacion.

### 5.2 Flujo core

```
CIERRE DE FAENA/PROYECTO:

1. Supervisor abre la app en su celular (2 min por trabajador)
2. Ve la lista de trabajadores del proyecto
3. Por cada trabajador, evalua 5 dimensiones (1-5 estrellas):
   - Calidad de trabajo
   - Cumplimiento de seguridad
   - Puntualidad / asistencia
   - Trabajo en equipo
   - Habilidad tecnica
4. Comentario rapido (opcional, puede ser voz a texto)
5. Marca: Recontratarias? [Si / Con reservas / No]
6. Si "No": motivo (ausentismo, seguridad, calidad, actitud, otro)

ARMADO DE CUADRILLA PARA NUEVO PROYECTO:

1. Busca: Especialidad = Soldador 4G
2. Filtra: Score >= 3.5, Seguridad >= 4, Disponible
3. Ve historial de cada uno + tendencia entre proyectos
4. IA sugiere cuadrilla optima basada en desempeno y compatibilidad
5. Alertas: trabajadores con patrones negativos o vencimientos
```

### 5.3 Diferenciadores y moat

1. **Historial acumulativo**: Cada evaluacion suma. Despues de 6 meses, hay data irreemplazable. Switching cost altisimo.
2. **IA para insights**: "Proyectos con Juan Perez tuvieron 15% menos re-trabajo en soldadura".
3. **Integracion ChileValora**: Perfiles de competencias como baseline + evaluacion continua encima.
4. **Reemplazo legal de listas negras**: Sistema transparente, incluido en Reglamento Interno, cumple normativa DT.
5. **Mobile-first para terreno**: Funciona con senal intermitente (offline-first), interfaz simple, 2 minutos por evaluacion.

### 5.4 Stack tecnico

Reutiliza ~60-70% de la infraestructura existente de otros proyectos:

| Componente | Tecnologia | Reutilizado de |
|---|---|---|
| Backend | FastAPI + Python 3.11+ | CasiListo, Analisis Licitaciones |
| Frontend | React 19 + TypeScript + Tailwind v4 | CasiListo |
| Base de datos | PostgreSQL (Supabase) | CasiListo |
| IA / Insights | OpenAI GPT-4o | Multiples proyectos |
| Alertas | WhatsApp Bot | Bot Faymex existente |
| Deploy | Railway (backend) + Vercel (frontend) | CasiListo |

---

## 6. Modelo de negocio

### 6.1 Pricing

| Plan | Trabajadores activos | Precio | Target |
|---|---|---|---|
| Gratis "Capataz" | Hasta 15 · 1 proyecto | $0 | Captacion (probar en una faena) |
| **Profesional "Faena"** | Hasta 100 · proyectos ilimitados | **$49.990 CLP/mes** | Contratista chico-mediano |
| Empresa "Contratista" | Hasta 500 · multi-faena | **$149.990 CLP/mes** | Contratista grande |
| Enterprise | +500 | Cotizacion | Multi-empresa / holding |

Supervisores e historico ilimitados en todos los planes. Eje de cobro: **trabajadores activos** (ver `PROPUESTA_MONETIZACION.md` y `ESTUDIO_PRECIOS_INVERSOR.md`).

### 6.2 Argumento de ROI

> "Si evitas recontratar a 3 malos trabajadores por ano, ahorras ~$4,5M CLP (a ~$1,5M por reemplazo evitado). El plan Profesional cuesta ~$600K CLP/ano. **ROI sobre 7x** — y mucho mayor si se evita un solo incidente de seguridad o la perdida de un contrato en faena minera."

### 6.3 Mercado

| Metrica | Valor |
|---|---|
| TAM (todos los contratistas Chile) | ~USD $3-18M/ano |
| SAM (contratistas medianos 20-200 trabajadores) | ~USD $2-3M/ano |
| SOM (capturables ano 1-2, 100-200 clientes) | ~USD $100-200K/ano |
| Expansion LATAM (Peru, Colombia, Mexico) | Multiplica x5-10 |

---

## 7. Ventajas competitivas de German / Faymex

1. **Faymex ES un contratista industrial** — German vive este dolor a diario. Ningun fundador de Buk o GeoVictoria tiene eso.
2. **Primer cliente = Faymex**: implementacion interna, datos reales, iteracion rapida antes de vender.
3. **Red de contactos**: 500+ contactos industriales en HubSpot, relaciones con mineras, proveedores del rubro.
4. **Stack tecnico probado**: 6+ proyectos en produccion con FastAPI + React + OpenAI + Railway.
5. **Dominio regulatorio**: conocimiento de SICEP, SERNAGEOMIN, Ley 20.123, ChileValora.
6. **Sinergia con pipeline de proyectos**: AcreditaMinero (documentos) + FaenaScore (desempeno) = suite completa.

---

## 8. Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Resistencia cultural ("siempre lo hicimos asi") | Alta | Alto | Empezar con Faymex, demostrar ROI real con numeros |
| Supervisores no evaluan (flojera) | Alta | Alto | 2 min mobile, obligatorio post-faena, voz a texto |
| Preocupacion legal de trabajadores | Media | Medio | Incluir en Reglamento Interno, cumplir DT, transparencia |
| Buk/Talana agregan modulo blue-collar | Baja | Medio | Estan enfocados en oficina; no entienden faena |
| Privacidad datos personales | Media | Medio | Ley 19.628, consentimiento informado, solo datos laborales |
| Mercado Chile acotado | Media | Medio | Expansion a Peru/Colombia/Mexico (misma industria) |

---

## 9. Plan de ejecucion

### Fase 1: MVP (3-4 semanas)
- Backend: API de evaluacion + base de datos de trabajadores
- Frontend: App mobile-responsive para evaluacion rapida
- Busqueda y filtrado de trabajadores por especialidad + score
- Deploy en Railway + Vercel

### Fase 2: Validacion interna (2 semanas)
- Implementar en Faymex con datos reales
- Evaluar trabajadores de ultimos 2-3 proyectos (retroactivo)
- Iterar UX con feedback de supervisores reales

### Fase 3: Primeros clientes (4-6 semanas)
- 5-10 contratistas conocidos de la red Faymex
- Landing page + demo
- Pricing validado

### Fase 4: IA + Insights (post-validacion)
- Sugerencias de cuadrilla optima
- Alertas de patrones negativos
- Integracion ChileValora
- Modulo de alertas WhatsApp

---

## 10. Conclusion

FaenaScore no es un "wrapper de IA" generico ni una copia de herramientas existentes. Es una solucion a un problema real, cuantificable y no resuelto en Chile ni LATAM, identificado desde la experiencia directa de operar una empresa contratista industrial.

El mercado de trabajadores subcontratados en Chile supera el millon de personas, las decisiones de recontratacion se toman con WhatsApp y memoria, y el costo de malas contrataciones es de decenas de millones de pesos anuales por empresa.

No hay competencia directa. La tecnologia necesaria ya existe y esta probada. El primer cliente esta asegurado (Faymex). El potencial de expansion a LATAM es natural.

**Score final: 8.5/10**

---

*Documento generado el 11 de abril de 2026 como parte del proceso de evaluacion de oportunidades micro-SaaS.*
*Basado en investigacion de mercado con multiples agentes de IA, validacion contra datos publicos (INE, SII, DT, SERNAGEOMIN, ChileValora), y experiencia directa del fundador.*
