import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ClipboardCheck, TrendingUp, History, ShieldCheck, Zap, Users, Check } from 'lucide-react'

interface LandingProps {
  isSignedIn: boolean
}

export default function Landing({ isSignedIn }: LandingProps) {
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
          <Link
            to={primaryCta.to}
            className="text-sm font-medium px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors"
          >
            {primaryCta.label}
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-4 md:px-6 py-12 md:py-24 text-center">
        <motion.h2 {...heroIn(0)} className="text-3xl md:text-5xl font-bold text-gray-900 tracking-tight leading-tight">
          Deja de recontratar
          <br className="hidden md:block" />
          <span className="text-blue-600"> al que ya te falló.</span>
        </motion.h2>
        <motion.p {...heroIn(1)} className="mt-5 md:mt-6 text-base md:text-xl text-gray-600 max-w-xl md:max-w-2xl mx-auto leading-relaxed">
          Tu próximo proyecto es tan bueno como la gente que vuelve. Recontrata recuerda
          quién rindió y quién no, para que repitas a tus mejores y dejes fuera al problema.
          Todo desde el celular, en terreno — con datos reales, no memoria ni WhatsApp.
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

        {/* Product preview */}
        <motion.div {...heroIn(3)} className="mt-12 md:mt-16 relative">
          <div className="absolute inset-x-0 top-1/2 -bottom-4 bg-gradient-to-b from-blue-50 to-transparent blur-3xl -z-10" aria-hidden="true" />
          <img
            src="/dashboard-preview.png"
            alt="Vista previa del Dashboard de Recontrata mostrando KPIs, top trabajadores y evaluaciones recientes."
            width={1440}
            height={900}
            loading="eager"
            className="w-full max-w-5xl mx-auto rounded-xl shadow-2xl border border-gray-200"
          />
        </motion.div>
      </section>

      {/* Problem */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-4xl mx-auto px-4 md:px-6 text-center">
          <h3 className="text-2xl md:text-3xl font-bold text-gray-900">
            Más de 1 millón de trabajadores subcontratados en Chile.
          </h3>
          <p className="mt-4 text-lg text-gray-600">
            Un trabajador que rinde mal no solo atrasa: cuesta retrabajos, días perdidos y,
            en terreno, hasta un accidente. Hoy la mayoría decide a quién recontratar por
            memoria del supervisor y cadenas de WhatsApp. Resultado: el mismo problema
            vuelve en el siguiente proyecto.
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
            title="El historial que no se va con el supervisor"
            body="Quién trabajó dónde y con qué desempeño queda registrado. Importa tu base desde Excel y empieza hoy."
          />
          <FeatureCard
            icon={ShieldCheck}
            title="Tu base de gente, solo tuya"
            body="Aislamiento por empresa: tus datos no se cruzan con otros contratistas. Tu activo más valioso, protegido."
          />
          <FeatureCard
            icon={Zap}
            title="Hecho para el celular del supervisor"
            body="Pensado para usarse en terreno, con una mano y guantes puestos. Funciona desde cualquier celular."
          />
          <FeatureCard
            icon={Users}
            title="Trae tu gente desde Excel"
            body="Sube tu planilla de trabajadores en Excel o CSV. RUT validado automáticamente."
          />
        </div>
      </section>

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
              cta="Contactar"
              ctaTo="mailto:contacto@recontrata.cl?subject=Plan%20Empresa"
              external
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
            Construye tu mejor equipo, proyecto tras proyecto.
          </h3>
          <p className="mt-4 text-blue-100 text-lg">
            Crea tu organización gratis. Sin tarjeta de crédito.
          </p>
          <Link
            to={primaryCta.to}
            className="mt-8 inline-block px-8 py-3 rounded-lg bg-white text-blue-600 font-medium hover:bg-blue-50 transition-colors"
          >
            {primaryCta.label}
          </Link>
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
