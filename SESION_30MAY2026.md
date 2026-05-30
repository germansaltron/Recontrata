# Bitácora de sesión — 30 de mayo 2026

> Proyecto: **FaenaScore → Recontrata** (SaaS de evaluación de desempeño de trabajadores de faena, Chile + pan-LATAM).
> Path: `C:\Users\Usuario\Claude Code German\FaenaScore` · Repo: `github.com/German-Faymex/FaenaScore` · Prod: `https://faenascore-production.up.railway.app`
> Sesión larga y muy productiva. Este documento consolida TODO lo realizado hoy.

---

## 0. Resumen ejecutivo

Cinco grandes bloques de trabajo, todos cerrados o avanzados:

| # | Bloque | Estado |
|---|--------|--------|
| 1 | **Monetización**: investigación de competidores + modelo + precios | ✅ Decidido y deployado a la landing |
| 2 | **Performance**: latencia de "Evaluar" 4-5s | ✅ Resuelto (N+1 + prefetch/caché) → se siente instantáneo |
| 3 | **Rebrand** FaenaScore → **Recontrata** (por expansión pan-LATAM) | ✅ Fase A (código) deployada · ⏳ Fase B (infra) en curso |
| 4 | **Dominio** `recontrata.cl` vía Cloudflare | ⏳ Configurado, esperando propagación DNS |
| 5 | **Logo + animación** de Recontrata | 🟡 Logo elegido + animación hecha · ❌ PENDIENTE: punta de la flecha |

---

## 1. Monetización

### Investigación (web + análisis)
- **Chile**: todo el ecosistema HR-tech cobra **por trabajador/mes** (Buk, Talana, Rankmi, GeoVictoria). Buk no publica precios (solo cotización) y "Gestión del Desempeño" es un **módulo aparte**. No hay competidor directo del nicho "¿debería volver a la faena?".
- **Global**: Workyard US$6-13/usuario + **US$50 base fee** (criticado por empresas con fuerza laboral fluctuante = perfil de Recontrata). Performance casi siempre es add-on (BambooHR/Lattice/15Five).
- **Freemium vs trial**: trial convierte mejor (14-25% vs 2-5% freemium), pero el "momento ajá" de Recontrata (armar la 2ª cuadrilla filtrando por desempeño) tarda >14 días → conviene **híbrido**. La **activación** es el predictor #1, no el precio.

### Decisiones (confirmadas por Germán)
- **Eje de cobro**: flat por **"trabajadores activos"**, con **supervisores e historial ilimitados** (el dato es el moat; cobrar por seat penaliza la adopción que lo genera).
- **Conversión**: híbrido **freemium + trial 14 días**.
- **Design partners**: **10** a −50% de por vida.

### Tabla de precios FINAL (deployada en la landing)
| Plan | Trabajadores activos | Precio/mes |
|---|---|---|
| Gratis "Capataz" | 15 · 1 proyecto | $0 |
| **Profesional** ⭐ | hasta 100 | **$49.990** (subido desde $29.990) |
| Empresa | hasta 500 | **$149.990** |
| Enterprise | +500 | Cotización |

Anual = 2 meses gratis. Pago: transferencia+factura (clave B2B Chile) + Webpay.

📄 Detalle completo: **`PROPUESTA_MONETIZACION.md`**.

---

## 2. Performance — latencia de "Evaluar"

### Síntoma
Entrar a "Evaluar" tardaba **4-5 s**.

### Diagnóstico (medido)
- **N+1 anidado**: `Evaluate.tsx` llamaba `listProjectWorkers` por cada proyecto (1+N), y el backend `list_project_workers` hacía 1 query de evaluación **por cada trabajador** (1+M) → **40-60 queries secuenciales**.
- Además `list_projects` hacía 2 queries por proyecto.
- Medición de latencia base: **~0.5 s por query** a Supabase (São Paulo) + ~0.5 s de RTT (servidor Railway probablemente en EE.UU. + `statement_cache_size=0`).

### Solución (2 capas)
1. **Backend (eliminar N+1)** — commit `adc3477`:
   - `list_project_workers` → single query con `outerjoin` a Evaluation.
   - `list_projects` → subqueries escalares correlacionadas (1 query).
   - Nuevo endpoint `GET /dashboard/projects-pending` (2 queries fijas) que reemplaza el fan-out del frontend.
   - `Evaluate.tsx` → 1 sola llamada agregada.
   - Resultado verificado: 4-5 s → **~2 s**. También aceleró Proyectos y Detalle de Proyecto.
2. **Cliente (que se sienta instantáneo)** — commits `c8c83be` + `af0e26f`:
   - `lib/swr.ts`: caché en memoria stale-while-revalidate.
   - `AppShell` precarga (prefetch) los datos de Evaluar + su chunk JS al entrar a cualquier pantalla del panel.
   - `Evaluate.tsx` renderiza la caché al instante y revalida.
   - Resultado confirmado por Germán: **"se siente bien"** (instantáneo en el flujo normal).

### Nota honesta
Hay un **piso físico de ~300-500 ms** por la base en Brasil + auth por request. Para bajar el número duro a futuro: **session pooler de Supabase** (baja cada query de ~0.5 s a ~0.15 s) — requiere la connection string del session pooler. Pendiente opcional.

---

## 3. Rebrand: FaenaScore → Recontrata

### Por qué
Germán quiere expandir a **toda Latinoamérica**. La palabra **"Faena" no viaja**:
- ✅ Chile / Perú / Bolivia (andino-minero): jerga del rubro.
- ❌ **Argentina / Uruguay**: "faena" = **matanza/sacrificio de ganado** (matadero-frigorífico, acepción oficial SENASA).
- ⚠️ México / Colombia: tarea coloquial / taurino / agrícola, no construcción.

→ Se descartó FaenaScore **y** FichaFaena (ambos anclados a "Faena"). Tras explorar opciones pan-LATAM con dominios, Germán eligió **Recontrata** (la propuesta de valor, universal, sin connotación negativa). `recontrata.cl` estaba libre.

### Fase A — Código (HECHA, deployada) — commit `267c170`
`sed` de `FaenaScore`→`Recontrata` y `faenascore.cl`→`recontrata.cl` en 9 archivos (Landing, AppShell, Terms, Privacy, EvaluateWorker, index.html, config.py, main.py, dependencies.py). Emails → `contacto@recontrata.cl`.
- **Infraestructura intacta a propósito**: `faenascore-production.up.railway.app`, nombres de DB y CORS NO se tocaron (es Fase B).
- Verificado en prod: `<title>Recontrata</title>` vivo, build OK, 21 tests OK.

### Fase B — Infraestructura (decisión de Germán: "solo conectar dominio")
- Repo GitHub y proyecto Railway **se dejan como `faenascore-*`** (son internos, no se ven). Rename cosmético postergado.
- Pendiente menor: regenerar `dashboard-preview.png` (la captura de la landing aún muestra el logo viejo) y el favicon.

---

## 4. Dominio recontrata.cl (Cloudflare)

- Dominio **comprado** por Germán en NIC Chile.
- DNS gestionado por **Cloudflare** (mismo patrón que soymaestra.cl).
- **Railway**: `recontrata.cl` y `www` registrados como dominios custom del servicio.
- **NIC**: nameservers cambiados a `cash.ns.cloudflare.com` + `romina.ns.cloudflare.com` (confirmado en whois oficial).
- **Cloudflare DNS** (4 registros, verificados en captura):
  - CNAME `@` → `m64rjt83.up.railway.app` (Proxied 🟠)
  - CNAME `www` → `f7aamsm6.up.railway.app` (Proxied 🟠)
  - TXT `_railway-verify` → hash `ebfb7af7…`
  - TXT `_railway-verify.www` → hash `a98797d0…`
- **Estado**: zona "pending" en Cloudflare; `recontrata.cl` aún no resuelve en DNS públicos → **propagación en curso** (típico 15 min–2 h en `.cl`).

### Pendiente cuando propague
1. Verificar que Cloudflare active la zona + Railway emita el SSL + `https://recontrata.cl` cargue.
2. Cloudflare **SSL/TLS → Full** (verificar).
3. **Clerk** (dashboard): agregar `recontrata.cl` + `www` a orígenes permitidos (si no, el login falla).

---

## 5. Logo + animación de Recontrata

### Logo
- Se generaron **3 conceptos** (estrella / flecha de retorno / estrella+ciclo) en estilo del sistema de Casilisto. Germán y yo coincidimos en el **concepto B = flecha de retorno** (cuadro azul `#2563eb` + flecha circular blanca + wordmark **"Re"** azul + **"contrata"** gris). El "Re" + flecha de retorno = recontratar.
- Assets en `branding/`: `logo-recontrata.svg`, `logo-preview.html`.

### Animación "el ciclo se cierra"
Secuencia: el cuadro aparece → la flecha se traza girando → la punta → giro de cierre del ciclo → entra el wordmark.
- **Web** (SVG + CSS): `branding/logo-animado/index.html` (servida localmente en `http://127.0.0.1:8077/branding/logo-animado/index.html`).
- **Video** (Pillow, reproducible): `branding/logo-animado/animate_logo.py` → MP4 + GIF, fondo claro y oscuro, en `branding/logo-animado/output/`.

### ❌ PENDIENTE CRÍTICO (mañana): la punta de la flecha
- Germán reportó **2 veces** que la punta de la flecha está mal en el video.
- Intentos fallidos: (1) "L" axis-aligned en PIL; (2) chevron tangente en PIL — **sigue mal**.
- **Para retomar**:
  1. **Aclarar con Germán qué exactamente está mal**: ¿solo el render del video (PIL)?, ¿también el símbolo SVG (Lucide rotate-ccw)?, ¿es la punta, el ángulo, el gap, el grosor?
  2. **Estrategia técnica sugerida**: dejar de dibujar la flecha a mano en PIL y **rasterizar el SVG real por frame** (resvg/cairosvg), animando `stroke-dashoffset`. El SVG web usa el path correcto de Lucide y se ve bien; el problema es la reconstrucción manual en el video. Alternativa: rediseñar el símbolo de flecha desde cero si a Germán no le convence el de Lucide.

---

## 6. Estado de producción (fin de jornada)

- **App viva**: `https://faenascore-production.up.railway.app` — marca **Recontrata**, precios nuevos, performance optimizada. `/api/health` OK.
- **Dominio** `recontrata.cl`: propagando (no carga aún).
- **Branch**: `master`, todo pusheado. Último commit `c4727c6`.

---

## 7. Pendientes para la próxima sesión (priorizados)

1. **🎨 Arreglar la punta de la flecha del logo** (lo que quedó abierto hoy) — ver §5.
2. **🌐 Verificar `recontrata.cl`**: propagación + SSL + carga + Clerk (orígenes) + SSL Full en Cloudflare.
3. **🖼️ Exportar set de assets** del logo (favicon, ícono PWA, og-image) e **integrar la animación** como intro en la landing; reemplazar el favicon viejo de FaenaScore.
4. **🔐 Clerk producción** (quita el banner "Development mode") — ahora destrabado por el dominio.
5. **⚡ (Opcional) Session pooler de Supabase** para bajar el número duro de latencia.
6. **📣 Plan de los 10 design partners** (precio fundador −50% lifetime) + go-to-market 1:1.

---

## 8. Datos técnicos clave (referencia rápida)

- **Railway**: proyecto `faenascore` (id `7ec526bb-74bc-4796-bac4-4c89bde2d6bd`), servicio `faenascore` (id `a5ff98e5-da2f-4d72-a7d9-05217565e1fc`), env production. Cuenta `bodegaquilp01@gmail.com`.
- **Deploy** (sin autodeploy desde GitHub): `railway link` → **`railway service faenascore`** (imprescindible) → `railway up --detach`. Verificar pollando el bundle/endpoint real, no solo `/health`.
- **Supabase**: ref `sudhcjpiixkkwywapvpe` (sa-east-1).
- **Dominio**: `recontrata.cl` (Cloudflare NS `cash`/`romina.ns.cloudflare.com`; CNAMEs a `m64rjt83`/`f7aamsm6.up.railway.app`).
- **Branding**: `branding/logo-recontrata.svg`, `branding/logo-animado/` (index.html + animate_logo.py + output/).

## 9. Commits del día (principales)
- Monetización: `3016bc5` (pricing landing) + docs.
- Performance: `adc3477` (N+1 backend) · `c8c83be` + `af0e26f` (prefetch/caché).
- Rebrand: `267c170` (FaenaScore→Recontrata, código).
- Branding: `c4727c6` (logo B + animación; punta pendiente).
- (+ varios `docs: PROGRESS …` intercalados.)

---

*Documento generado al cierre de la sesión del 30-may-2026. Ver `PROGRESS.md` para el detalle cronológico y los archivos de memoria (`faenascore_monetizacion.md`, `faenascore_railway_deploy.md`, `recontrata_rebrand_dominio.md`).*
