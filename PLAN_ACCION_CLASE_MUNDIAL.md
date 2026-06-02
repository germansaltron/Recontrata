# Recontrata — Plan de Acción "Clase Mundial"

> Síntesis de auditoría multi-rol (UX · Marketing · RRHH/Legal · Ciberseguridad) — 1 jun 2026.
> Objetivo: pulir el sistema de pre-lanzamiento a producto pan-LATAM de clase mundial.

## Diagnóstico en una línea por experto

- **UX**: base sólida y consistente, pero falla para el uso real en terreno (targets táctiles chicos, sin bottom-nav, sin toasts, sin offline) y tiene dead-ends silenciosos.
- **Marketing**: posicionamiento diferenciado pero la landing "describe" en vez de "vender": cero prueba social, ROI ($750K) ausente, SEO vacío, precios solo CLP.
- **RRHH/Legal**: la metodología del score (promedio plano de 5 dims) es indefendible y hay riesgo legal serio (Ley 21.719, consentimiento del trabajador, score portable, sin derecho a réplica).
- **Ciberseguridad**: estructura razonable, pero hay 3 bloqueantes pre-lanzamiento (defaults inseguros dependientes de Railway, endpoint admin destructivo, IDOR cross-tenant).

## Temas que CRUZAN a varios expertos (atacar primero — máximo apalancamiento)

1. **Pan-LATAM no es real todavía** (UX+Mkt+RRHH): RUT hardcodeado como identificador único, precios solo CLP, copy/legal "en Chile". Bloquea la promesa central.
2. **Confianza/legal** (Mkt+RRHH): disclaimer "Borrador inicial" en Privacy/Terms en producción + ley citada derogada (19.628 vs 21.719).
3. **El score se muestra como promedio sin detalle** (UX+RRHH): no se ven las 5 dimensiones en el historial → decisiones sobre un número opaco.

---

## FASE 0 — Bloqueantes de seguridad (ANTES de abrir registro) · ~3-4h

| # | Acción | Archivo | Sev |
|---|--------|---------|-----|
| S1 | Voltear defaults: `AUTH_MOCK_ENABLED=False`, `DEBUG=False` + **confirmar ambas en Railway** | `config.py:11,17` | CRÍTICA |
| S2 | Proteger/eliminar `/admin/seed-demo/{org_id}` (borra datos de cualquier org); exigir ADMIN_TOKEN ≥32 chars en startup | `api/v1/admin.py` | CRÍTICA |
| S3 | Fix IDOR `unassign_worker`: filtrar por `Project.org_id == org_id` | `api/v1/projects.py:168` | CRÍTICA |
| S4 | Fix defensa en profundidad `list_project_workers`: agregar `Worker.org_id == org_id` | `api/v1/projects.py:185` | ALTA |
| S5 | `sort_by` con allowlist (no `getattr` dinámico) | `api/v1/workers.py:75` | ALTA |
| S6 | Validar upload Excel: content-type, tamaño máx (5MB), límite de filas | `api/v1/workers.py:163` | ALTA |
| S7 | Migrar Clerk dev → producción (requiere a Germán: instancia prod + DNS) | Railway/Clerk | ALTA |
| S8 | Security headers (X-Frame-Options, nosniff, HSTS, Referrer-Policy) + CORS methods/headers explícitos + rate limiting (SlowAPI) | `main.py` | MEDIA |

## FASE 1 — Confianza y riesgo legal · ~1 sprint

| # | Acción | Origen |
|---|--------|--------|
| L1 | Quitar disclaimer "Borrador inicial" de Privacy/Terms; citar **Ley 21.719** (no 19.628) | Mkt P0 + RRHH P1 |
| L2 | `rehire_reason` OBLIGATORIO en backend cuando `would_rehire != "yes"` (hoy solo valida el front) | RRHH P2 |
| L3 | Soft-delete + audit log en evaluaciones (hoy DELETE físico sin traza) | RRHH P1 + Sec |
| L4 | Consentimiento del trabajador: tabla `worker_consent`; separar perfil intra-org vs cross-org | RRHH P0 |
| L5 | Time-lock de edición de evaluaciones (72h) + versionado | RRHH P2 |

## FASE 2 — Conversión (landing) · quick wins, <1 día

| # | Acción | Origen |
|---|--------|--------|
| M1 | `<title>` + meta description + OG con keyword y propuesta de valor | Mkt P0 |
| M2 | Sección de prueba social (caso 0 Faymex / stat-bar INE + "$750K por mala recontratación") | Mkt P0 |
| M3 | Inyectar el ROI concreto ($750K) en hero y bajo el precio Profesional | Mkt P0 |
| M4 | Ángulo "la alternativa legal a las listas negras" (diferenciador pan-LATAM) | Mkt apuesta |
| M5 | Nav links (Funciones/Precios) + 2º CTA + CTA de cierre con urgencia | Mkt P2 |
| M6 | Plan Empresa: CTA self-serve (trial) en vez de `mailto:` | UX P2 + Mkt P1 |

## FASE 3 — UX de terreno · ~1 sprint

| # | Acción | Origen |
|---|--------|--------|
| U1 | Bottom-nav bar en móvil (Evaluar a 1 tap) | UX P1 |
| U2 | Toast system (Sonner) + eliminar `alert()` | UX P0 |
| U3 | Targets táctiles de estrellas a ~68px (guantes) | UX P0 |
| U4 | Recuperar dead-end de creación de org (estado error + retry) | UX P0 |
| U5 | Vista de cards de trabajadores en móvil | UX P0 |
| U6 | Post-evaluación: "Evaluar siguiente pendiente" + toast éxito | UX P1 |
| U7 | Mostrar las 5 dimensiones en historial + export CSV (no solo promedio) | UX+RRHH |
| U8 | Anclas de comportamiento (BARS) por dimensión en el form | RRHH P1 |
| U9 | Skeletons/errores consistentes (WorkerDetail, ProjectDetail, Dashboard) + a11y modal/StarRating | UX P1/P2 |

## FASE 4 — Pan-LATAM (habilita la promesa) · arquitectónico

| # | Acción | Origen |
|---|--------|--------|
| P1 | Abstraer identificador: `id_type` + `id_country` (RUT→CURP/DNI/Cédula/CUIL); romper `uq_worker_org_rut` | UX+RRHH+Mkt |
| P2 | Pricing dual CLP/USD + detección de país; quitar "pesos chilenos" del título | Mkt P1 |
| P3 | Términos/Privacidad por jurisdicción (CL/PE/CO/MX/AR) | RRHH P3 |
| P4 | Copy sin chilenismos ni "faena" (ya iniciado en hero) | Mkt P1 |

## FASE 5 — Apuestas grandes (diferenciación clase mundial)

1. **Motor de score defensible**: ponderación por industria (Seguridad 25-40% en minería), decay temporal, detección de evaluaciones sospechosas, fórmula pública (transparencia art. 16 Ley 21.719). *(RRHH+convierte riesgo legal en feature)*
2. **Portal del Trabajador**: transparencia + derecho a réplica + opt-out + certificado descargable → de "herramienta del contratista" a "activo del trabajador" (el LinkedIn de la faena). *(RRHH, neutraliza el mayor riesgo legal)*
3. **Offline-first en terreno**: service worker + cola IndexedDB + sync. Diferenciador real en minas sin señal. *(UX)*
4. **Módulo anti-sesgo / calibración de evaluadores** (leniencia, halo, disparidad inter-evaluadores). *(RRHH)*
5. **Tests de aislamiento multi-tenant como CI gate** + auditoría PII. *(Seguridad)*

---

### Secuencia recomendada
**FASE 0 (seguridad) → FASE 1 (legal) → FASE 2 (conversión) → FASE 3 (UX terreno) → FASE 4 (pan-LATAM) → FASE 5 (apuestas).**
Las Fases 0-2 deben cerrarse antes del lanzamiento público. 3-4 en paralelo a beta. 5 es roadmap.
