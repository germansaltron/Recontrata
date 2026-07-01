import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ClipboardCheck, TrendingUp, History, ShieldCheck, WifiOff, Users, Check, PlayCircle } from 'lucide-react'
import { getTutorial, type Tutorial } from '../lib/tutorials'
import { TutorialModal } from '../components/ui/TutorialModal'

interface LandingProps {
  isSignedIn: boolean
}

export default function Landing({ isSignedIn }: LandingProps) {
  const [demo, setDemo] = useState<Tutorial | null>(null)
  const primaryCta = isSignedIn
    ? { to: '/app', label: 'Ir al Dashboard' }
    : { to: '/sign-in', label: 'Empezar gratis' }

  // Entrada suave del hero (el splash del logo cubre la pantalla mientras carga).
  const heroIn = (i: number) => ({
    initial: { opacity: 0, y: 16 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5, delay: 0.1 + i * 0.1 },
  })

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-gray-200 bg-white/85 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-4 md:px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center" aria-label="Recontrata — inicio">
            <img
              id="nav-logo"
              src="/logo-recontrata.png"
              alt="Recontrata"
              className="h-8 w-auto"
            />
          </Link>
          <nav className="flex items-center gap-2 sm:gap-5">
            <a href="#features" className="hidden md:inline text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors">
              Funciones
            </a>
            <a href="#pricing" className="hidden md:inline text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors">
              Precios
            </a>
            {!isSignedIn && (
              <Link to="/sign-in" className="hidden sm:inline text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors">
                Iniciar sesión
              </Link>
            )}
            <Link
              to={primaryCta.to}
              className="text-sm font-medium px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors"
            >
              {primaryCta.label}
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-4 md:px-6 py-12 md:py-24 text-center">
        <motion.h2 {...heroIn(0)} className="text-3xl md:text-5xl font-bold text-gray-900 tracking-tight leading-tight">
          Tu mejor equipo,
          <br className="hidden md:block" />
          <span className="text-blue-600"> en cada proyecto.</span>
        </motion.h2>
        <motion.p {...heroIn(1)} className="mt-5 md:mt-6 text-base md:text-xl text-gray-600 max-w-xl md:max-w-2xl mx-auto leading-relaxed">
          La gente que vuelve es lo que hace grande a tu próximo proyecto. Recontrata recuerda
          quién rindió y te ayuda a repetir a tus mejores trabajadores, proyecto tras proyecto.
          Todo desde el celular, en terreno y hasta sin señal — con datos reales, no con recuerdos ni mensajes de WhatsApp.
        </motion.p>
        <motion.div {...heroIn(2)} className="mt-8 md:mt-10 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            to={primaryCta.to}
            className="w-full sm:w-auto px-6 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
          >
            {primaryCta.label}
          </Link>
          <a
            href="#features"
            className="w-full sm:w-auto px-6 py-3 rounded-lg border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition-colors"
          >
            Ver cómo funciona
          </a>
        </motion.div>
        <motion.p {...heroIn(2)} className="mt-5 text-sm text-gray-500">
          Reemplazar a un mal operario cuesta <span className="font-semibold text-gray-700">~$1,5 millones</span>.
          Recontrata te ayuda a no repetir el error.
        </motion.p>

        {/* Product showcase: la faena + la app en el celular */}
        <motion.div {...heroIn(3)} className="mt-14 md:mt-20 relative max-w-5xl mx-auto">
          <div className="absolute -inset-x-4 top-1/3 -bottom-8 bg-gradient-to-b from-blue-50 to-transparent blur-3xl -z-10" aria-hidden="true" />
          <div className="rounded-2xl overflow-hidden shadow-2xl border border-gray-200">
            <img
              src="/hero-faena.jpg"
              alt="Mina a cielo abierto de gran minería."
              width={1600}
              height={727}
              loading="eager"
              className="w-full h-[220px] sm:h-[320px] md:h-[420px] object-cover"
            />
          </div>
          <img
            src="/phone-eval.png"
            alt="Evaluación de un trabajador en la app de Recontrata, desde el celular en terreno."
            width={540}
            height={955}
            loading="eager"
            className="absolute -bottom-8 right-2 sm:right-5 md:right-8 w-32 sm:w-48 md:w-64 drop-shadow-2xl"
          />
        </motion.div>
      </section>

      {/* Prueba social / stat-bar — el problema en cifras reales */}
      <section className="border-y border-gray-200 bg-gray-50 py-12 md:py-14">
        <div className="max-w-6xl mx-auto px-4 md:px-6">
          <p className="text-center text-xs md:text-sm font-semibold uppercase tracking-wide text-blue-600">
            El problema, en cifras reales
          </p>
          <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-4">
            <Stat value="1.071.128" label="trabajadores subcontratados en Chile" source="INE, 2024" />
            <Stat value="50%" label="rotación laboral en construcción, la más alta del país" source="INE" />
            <Stat
              value="~$1,5M"
              label="cuesta reemplazar a un operario que no debió volver"
              source="≈16-20% del salario anual · Center for American Progress (2012)"
              sourceHref="https://www.americanprogress.org/article/there-are-significant-business-costs-to-replacing-employees/"
            />
            <Stat value="2.854+" label="nombres en listas negras ilegales denunciadas en minería" source="Federación Minera / DT" />
          </div>
          <p className="mt-8 text-center text-sm text-gray-500 max-w-2xl mx-auto">
            Hoy esas decisiones se toman con memoria y WhatsApp. Recontrata las convierte en datos.
          </p>
        </div>
      </section>

      {/* Problem */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-4xl mx-auto px-4 md:px-6 text-center">
          <h3 className="text-2xl md:text-3xl font-bold text-gray-900">
            Tu mejor activo ya trabajó contigo.
          </h3>
          <p className="mt-4 text-lg text-gray-600">
            En cada proyecto hay gente que marca la diferencia: llega a tiempo, hace bien su trabajo
            y cuida al equipo. Hoy ese talento se diluye en la memoria del supervisor y en
            cadenas de WhatsApp. Recontrata lo convierte en tu ventaja: un historial de
            desempeño real que te acompaña proyecto tras proyecto.
          </p>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="max-w-6xl mx-auto px-4 md:px-6 py-16 md:py-24">
        <h3 className="text-2xl md:text-3xl font-bold text-gray-900 text-center">
          Evalúa en terreno. Decide con datos.
        </h3>
        <div className="mt-12 grid md:grid-cols-3 gap-6">
          <FeatureCard
            icon={ClipboardCheck}
            title="Evalúa en terreno, en 30 segundos"
            body="5 dimensiones (calidad, seguridad, puntualidad, equipo, técnica) + recomendación de recontratación. Desde el celular, sin parar el trabajo."
          />
          <FeatureCard
            icon={TrendingUp}
            title="Sabe quién rinde antes de contratar"
            body="Cada trabajador acumula un score real a través de tus proyectos. Ordena, filtra y encuentra a los mejores en segundos."
          />
          <FeatureCard
            icon={History}
            title="El historial que se queda contigo"
            body="Quién trabajó dónde y con qué desempeño queda registrado para siempre. Importa tu base desde Excel y empieza hoy."
          />
          <FeatureCard
            icon={ShieldCheck}
            title="Tu base de gente, solo tuya"
            body="Aislamiento por empresa: tus datos no se cruzan con otros contratistas. Tu activo más valioso, protegido."
          />
          <FeatureCard
            icon={WifiOff}
            title="¿Sin señal en terreno? Igual evalúas"
            body="En faena —una obra, una mina o cualquier lugar remoto— muchas veces no hay internet. Recontrata sigue funcionando sin conexión y envía las evaluaciones solo cuando vuelve la señal — no se pierde nada. Pensado para usarse con una mano y guantes puestos."
          />
          <FeatureCard
            icon={Users}
            title="Trae tu gente desde Excel"
            body="Sube tu planilla de trabajadores en Excel o CSV. RUT validado automáticamente."
          />
        </div>
      </section>

      {/* Panel web */}
      <section className="bg-white pt-4 pb-16 md:pb-20">
        <div className="max-w-6xl mx-auto px-4 md:px-6 text-center">
          <h3 className="text-2xl md:text-3xl font-bold text-gray-900">
            Y todo se ordena en un solo panel.
          </h3>
          <p className="mt-3 text-gray-600 max-w-2xl mx-auto">
            Proyectos, trabajadores, scores e historial. Ve de un vistazo a quién recontratar
            — desde el computador de la oficina.
          </p>
          <div className="mt-10 relative">
            <div className="absolute inset-x-0 top-1/2 -bottom-4 bg-gradient-to-b from-blue-50 to-transparent blur-3xl -z-10" aria-hidden="true" />
            <img
              src="/dashboard-preview.png"
              alt="Panel de Recontrata con KPIs, top trabajadores y evaluaciones recientes."
              width={1440}
              height={900}
              loading="lazy"
              className="w-full max-w-5xl mx-auto rounded-xl shadow-2xl border border-gray-200"
            />
          </div>
        </div>
      </section>

      {/* Diferenciador: alternativa legal a las listas negras */}
      <section className="bg-gray-900 py-16 md:py-20">
        <div className="max-w-4xl mx-auto px-4 md:px-6 text-center">
          <span className="inline-block text-xs font-semibold uppercase tracking-wide text-blue-400">
            La diferencia
          </span>
          <h3 className="mt-4 text-2xl md:text-4xl font-bold text-white leading-tight">
            La alternativa legal a las listas negras.
          </h3>
          <p className="mt-5 text-base md:text-lg text-gray-300 leading-relaxed max-w-2xl mx-auto">
            Las listas negras son ilegales y la Dirección del Trabajo las persigue, pero siguen
            existiendo porque no había una alternativa estructurada. Recontrata es esa alternativa:
            evaluaciones de desempeño objetivas, con motivo registrado, consentimiento del trabajador
            y derecho a réplica. Decisiones que puedes defender — no rumores que te exponen.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-sm text-gray-400">
            <span className="flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-blue-400" /> Criterios objetivos, no rumores</span>
            <span className="flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-blue-400" /> Consentimiento y derecho a réplica</span>
            <span className="flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-blue-400" /> Trazable y auditable</span>
          </div>
        </div>
      </section>

      {/* Míralo en acción (tutoriales) */}
      <section className="bg-white py-16 md:py-24">
        <div className="max-w-5xl mx-auto px-4 md:px-6 text-center">
          <h3 className="text-2xl md:text-3xl font-bold text-gray-900">Míralo en acción</h3>
          <p className="mt-3 text-base text-gray-600 max-w-2xl mx-auto">
            En menos de un minuto: cómo se ve por dentro y cómo se evalúa en pleno terreno.
          </p>
          <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 gap-6">
            {['clip1', 'clip5'].map((key) => {
              const t = getTutorial(key)
              if (!t) return null
              return (
                <button
                  key={key}
                  onClick={() => setDemo(t)}
                  className="group text-left bg-gray-50 border border-gray-200 rounded-2xl overflow-hidden hover:border-blue-300 hover:shadow-md transition"
                >
                  <div className="aspect-video bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center">
                    <PlayCircle className="w-14 h-14 text-white/90 group-hover:scale-110 transition" />
                  </div>
                  <div className="p-5">
                    <p className="text-xs font-medium text-blue-600">Tutorial · {t.duration}</p>
                    <h4 className="font-semibold text-gray-900 mt-0.5">{t.title}</h4>
                    <p className="text-sm text-gray-500 mt-1">{t.blurb}</p>
                  </div>
                </button>
              )
            })}
          </div>
        </div>
      </section>
      {demo && <TutorialModal tutorial={demo} onClose={() => setDemo(null)} />}

      {/* Pricing */}
      <section id="pricing" className="bg-gray-50 py-16 md:py-24">
        <div className="max-w-6xl mx-auto px-4 md:px-6">
          <h3 className="text-2xl md:text-3xl font-bold text-gray-900 text-center">
            Planes simples. Precios en pesos chilenos.
          </h3>
          <p className="mt-3 text-center text-gray-600">
            Pagas por trabajadores activos, no por usuario. Supervisores e historial ilimitados en todos los planes.
          </p>
          <div className="mt-10 grid md:grid-cols-3 gap-6">
            <PricingCard
              name="Gratis"
              price="$0"
              period="para siempre"
              description="Para probar la herramienta en un proyecto pequeño."
              features={[
                'Hasta 15 trabajadores activos',
                '1 proyecto activo',
                'Supervisores ilimitados',
                'Historial completo por trabajador',
                'Import / export Excel y CSV',
              ]}
              cta={primaryCta.label}
              ctaTo={primaryCta.to}
            />
            <PricingCard
              name="Profesional"
              price="$49.990"
              period="CLP / mes"
              description="Para contratistas con proyectos activos de forma permanente."
              featured
              features={[
                'Hasta 100 trabajadores activos',
                'Proyectos y supervisores ilimitados',
                'Búsqueda y filtros avanzados',
                'Alertas y exportación',
                '14 días de prueba gratis',
              ]}
              roi="Evita 3 malas recontrataciones al año y ahorras ~$4,5M. El plan cuesta ~$600K/año: ROI sobre 7x."
              cta={primaryCta.label}
              ctaTo={primaryCta.to}
            />
            <PricingCard
              name="Empresa"
              price="$149.990"
              period="CLP / mes"
              description="Para empresas con múltiples equipos y muchos trabajadores."
              features={[
                'Hasta 500 trabajadores activos',
                'Multi-proyecto y multi-usuario',
                'Acceso a la API e integraciones',
                'Insights con IA y onboarding asistido',
                'Soporte prioritario',
              ]}
              roi="14 días de prueba gratis. Sin tarjeta de crédito."
              cta={primaryCta.label}
              ctaTo={primaryCta.to}
            />
          </div>
          <p className="mt-8 text-center text-xs text-gray-500">
            ¿Más de 500 trabajadores? Tenemos plan Enterprise a medida —{' '}
            <a href="mailto:contacto@recontrata.cl?subject=Plan%20Enterprise" className="underline hover:text-blue-600">escríbenos</a>.
            Facturación mensual o anual (2 meses gratis). Precios en CLP, referenciales en fase de lanzamiento.
          </p>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-blue-600 py-16">
        <div className="max-w-3xl mx-auto px-4 md:px-6 text-center">
          <h3 className="text-2xl md:text-3xl font-bold text-white">
            Tu próxima cuadrilla se arma esta semana.
          </h3>
          <p className="mt-4 text-blue-100 text-lg">
            Ármala con datos, no con memoria. Empieza gratis hoy, sin tarjeta de crédito,
            y cada evaluación queda registrada para siempre.
          </p>
          <Link
            to={primaryCta.to}
            className="mt-8 inline-block px-8 py-3 rounded-lg bg-white text-blue-600 font-medium hover:bg-blue-50 transition-colors"
          >
            {primaryCta.label}
          </Link>
          <p className="mt-4 text-sm text-blue-200">
            Listo en minutos · Importa tu base desde Excel · 14 días de prueba en planes de pago
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-10">
        <div className="max-w-6xl mx-auto px-4 md:px-6">
          <div className="grid gap-8 md:grid-cols-3 text-sm">
            <div>
              <p className="font-semibold text-gray-900">Recontrata</p>
              <p className="mt-2 text-gray-500">Evaluación de desempeño de trabajadores para contratistas de minería y construcción.</p>
              <p className="mt-2 text-gray-400 text-xs">Hecho en Chile</p>
            </div>
            <div>
              <p className="font-semibold text-gray-900">Producto</p>
              <ul className="mt-2 space-y-1.5 text-gray-600">
                <li><a href="#features" className="hover:text-blue-600">Funciones</a></li>
                <li><a href="#pricing" className="hover:text-blue-600">Precios</a></li>
                <li><Link to={primaryCta.to} className="hover:text-blue-600">{primaryCta.label}</Link></li>
              </ul>
            </div>
            <div>
              <p className="font-semibold text-gray-900">Legal</p>
              <ul className="mt-2 space-y-1.5 text-gray-600">
                <li><Link to="/terminos" className="hover:text-blue-600">Términos de Servicio</Link></li>
                <li><Link to="/privacidad" className="hover:text-blue-600">Política de Privacidad</Link></li>
                <li><a href="mailto:contacto@recontrata.cl" className="hover:text-blue-600">contacto@recontrata.cl</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-6 border-t border-gray-100 text-xs text-gray-400 flex flex-col md:flex-row items-center justify-between gap-2">
            <p>© {new Date().getFullYear()} Recontrata. Todos los derechos reservados.</p>
            <p>Para contratistas de minería y construcción.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function PricingCard({
  name,
  price,
  period,
  description,
  features,
  roi,
  cta,
  ctaTo,
  featured,
  external,
}: {
  name: string
  price: string
  period: string
  description: string
  features: string[]
  roi?: string
  cta: string
  ctaTo: string
  featured?: boolean
  external?: boolean
}) {
  const buttonClass = featured
    ? 'bg-blue-600 text-white hover:bg-blue-700'
    : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
  const cardClass = featured
    ? 'relative bg-white rounded-xl border-2 border-blue-600 p-6 shadow-sm'
    : 'relative bg-white rounded-xl border border-gray-200 p-6'
  return (
    <div className={cardClass}>
      {featured && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs font-semibold px-3 py-1 rounded-full">
          Más popular
        </span>
      )}
      <h4 className="text-lg font-semibold text-gray-900">{name}</h4>
      <div className="mt-4 flex items-baseline gap-2">
        <span className="text-3xl font-bold text-gray-900">{price}</span>
        <span className="text-sm text-gray-500">{period}</span>
      </div>
      <p className="mt-3 text-sm text-gray-600">{description}</p>
      {roi && (
        <p className={`mt-4 rounded-lg px-3 py-2 text-xs leading-relaxed ${featured ? 'bg-blue-50 text-blue-800' : 'bg-gray-50 text-gray-600'}`}>
          {roi}
        </p>
      )}
      <ul className="mt-5 space-y-2">
        {features.map((f) => (
          <li key={f} className="flex items-start gap-2 text-sm text-gray-700">
            <Check className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
            <span>{f}</span>
          </li>
        ))}
      </ul>
      {external ? (
        <a
          href={ctaTo}
          className={`mt-6 block w-full text-center px-4 py-2.5 rounded-lg font-medium transition-colors ${buttonClass}`}
        >
          {cta}
        </a>
      ) : (
        <Link
          to={ctaTo}
          className={`mt-6 block w-full text-center px-4 py-2.5 rounded-lg font-medium transition-colors ${buttonClass}`}
        >
          {cta}
        </Link>
      )}
    </div>
  )
}

function Stat({ value, label, source, sourceHref }: { value: string; label: string; source: string; sourceHref?: string }) {
  return (
    <div className="text-center">
      <div className="text-2xl md:text-4xl font-bold text-gray-900 tracking-tight">{value}</div>
      <p className="mt-2 text-xs md:text-sm text-gray-600 leading-snug">{label}</p>
      <p className="mt-1 text-[11px] text-gray-400">
        {sourceHref ? (
          <a
            href={sourceHref}
            target="_blank"
            rel="noopener noreferrer"
            className="underline decoration-dotted underline-offset-2 hover:text-gray-600"
          >
            {source}
          </a>
        ) : (
          source
        )}
      </p>
    </div>
  )
}

function FeatureCard({ icon: Icon, title, body }: { icon: React.ElementType; title: string; body: string }) {
  return (
    <div className="p-6 rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-sm transition-all">
      <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
        <Icon className="w-5 h-5" />
      </div>
      <h4 className="mt-4 font-semibold text-gray-900">{title}</h4>
      <p className="mt-2 text-sm text-gray-600 leading-relaxed">{body}</p>
    </div>
  )
}
