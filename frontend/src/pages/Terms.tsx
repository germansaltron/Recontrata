import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'

export default function Terms() {
  return (
    <div className="min-h-screen bg-white">
      <header className="border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-4 md:px-6 h-16 flex items-center gap-3">
          <Link to="/" className="p-2 hover:bg-gray-100 rounded-lg" aria-label="Volver al inicio">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-xl font-bold text-gray-900">Recontrata</h1>
        </div>
      </header>
      <article className="max-w-3xl mx-auto px-4 md:px-6 py-10 md:py-16 prose prose-sm md:prose-base">
        <h1 className="text-3xl font-bold text-gray-900">Términos de Servicio</h1>
        <p className="text-sm text-gray-500">Última actualización: 4 de junio de 2026</p>

        <p className="mt-6">
          Estos Términos de Servicio ("Términos") regulan el uso de la plataforma Recontrata
          ("el Servicio"), marca operada por Saltronic SpA, RUT 78.462.524-9, con domicilio en
          Quilpué, Región de Valparaíso, Chile ("nosotros", "nuestro"). Al crear una
          cuenta o usar el Servicio, usted ("el Usuario") acepta estos Términos.
        </p>

        <h2 className="text-xl font-semibold mt-8">1. Objeto del Servicio</h2>
        <p>
          Recontrata es una plataforma web orientada a contratistas de minería y construcción
          en Chile, que permite registrar trabajadores, proyectos y evaluaciones de desempeño,
          con el fin de apoyar decisiones internas de recontratación.
        </p>

        <h2 className="text-xl font-semibold mt-8">2. Registro y cuenta</h2>
        <ul className="list-disc pl-5 space-y-1">
          <li>El Usuario debe entregar información veraz al registrarse.</li>
          <li>La cuenta es personal; el Usuario es responsable de la seguridad de sus credenciales.</li>
          <li>Podemos suspender o cerrar cuentas que infrinjan estos Términos o utilicen el Servicio de forma fraudulenta.</li>
        </ul>

        <h2 className="text-xl font-semibold mt-8">3. Uso aceptable</h2>
        <p>El Usuario se obliga a no:</p>
        <ul className="list-disc pl-5 space-y-1">
          <li>Usar el Servicio para fines ilícitos o que vulneren derechos de terceros.</li>
          <li>Realizar ingeniería inversa, descompilar o intentar vulnerar la seguridad de la plataforma.</li>
          <li>Cargar datos de terceros sin contar con base de licitud conforme a la Ley N° 21.719.</li>
          <li>Usar el Servicio para discriminar a trabajadores por razones no objetivas o en infracción al Código del Trabajo.</li>
        </ul>

        <h2 className="text-xl font-semibold mt-8">4. Datos ingresados por el Usuario</h2>
        <p>
          El Usuario es el responsable del tratamiento de los datos personales que ingrese en
          el Servicio (nombres, RUT, teléfono, email de trabajadores, evaluaciones). Nosotros
          actuamos como encargado del tratamiento conforme a la Ley N° 21.719.
          El Usuario declara contar con la base legal para tratar dichos datos y se obliga a
          informar a los titulares en los términos que exija la ley vigente.
        </p>

        <h2 className="text-xl font-semibold mt-8">5. Planes y pagos</h2>
        <ul className="list-disc pl-5 space-y-1">
          <li>Existen planes gratuitos y de pago, cuyas condiciones vigentes se publican en la página de precios.</li>
          <li>Los precios están expresados en pesos chilenos (CLP) e incluyen o excluyen IVA según se indique en cada plan.</li>
          <li>Durante la fase de lanzamiento, los precios son referenciales y podrían ajustarse con aviso previo de al menos 30 días.</li>
          <li>La falta de pago faculta a suspender el acceso al Servicio.</li>
        </ul>

        <h2 className="text-xl font-semibold mt-8">6. Propiedad intelectual</h2>
        <p>
          El software, diseño, marcas y contenido del Servicio son de nuestra propiedad o
          licenciados a nosotros. Los datos cargados por el Usuario siguen siendo de su
          propiedad; el Usuario nos otorga una licencia limitada para procesarlos con el único
          fin de prestar el Servicio.
        </p>

        <h2 className="text-xl font-semibold mt-8">7. Disponibilidad y limitación de responsabilidad</h2>
        <p>
          El Servicio se ofrece "tal como está", sin garantía de disponibilidad continua.
          Dentro de los límites permitidos por la ley, no seremos responsables por lucro
          cesante, daños indirectos ni por decisiones de recontratación tomadas por el
          Usuario a partir de los datos almacenados. Recontrata no califica ni certifica a
          trabajadores: es una herramienta de registro interno del contratista.
        </p>

        <h2 className="text-xl font-semibold mt-8">8. Terminación</h2>
        <p>
          El Usuario puede cancelar su cuenta en cualquier momento escribiendo a
          contacto@recontrata.cl. En caso de terminación, eliminaremos los datos dentro de un
          plazo razonable, salvo aquellos que debamos conservar por obligación legal.
        </p>

        <h2 className="text-xl font-semibold mt-8">9. Modificaciones</h2>
        <p>
          Podemos actualizar estos Términos. Los cambios relevantes serán informados por email
          o dentro del Servicio con una antelación mínima de 15 días antes de su entrada en
          vigor.
        </p>

        <h2 className="text-xl font-semibold mt-8">10. Ley aplicable y jurisdicción</h2>
        <p>
          Estos Términos se rigen por las leyes de la República de Chile. Cualquier
          controversia se someterá a los tribunales ordinarios de justicia con asiento en
          Santiago, sin perjuicio de los derechos irrenunciables del consumidor.
        </p>

        <h2 className="text-xl font-semibold mt-8">11. Contacto</h2>
        <p>
          Para consultas relacionadas con estos Términos, escríbanos a{' '}
          <a href="mailto:contacto@recontrata.cl" className="text-blue-600 hover:underline">
            contacto@recontrata.cl
          </a>
          .
        </p>
      </article>
    </div>
  )
}
