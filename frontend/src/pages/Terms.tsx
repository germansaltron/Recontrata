import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'

// Contrato de Suscripción y Términos de Servicio (B2B). Reemplaza los términos
// genéricos anteriores. La versión de este texto debe mantenerse sincronizada con
// CONTRACT_VERSION del backend (app/legal.py): al cambiar el contrato, subir la versión
// aquí y allá para que el gate de aceptación pida aceptar la versión nueva.
export const CONTRACT_VERSION = '1.0'
const EFFECTIVE_DATE = '22 de julio de 2026'

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
        <h1 className="text-3xl font-bold text-gray-900">Contrato de Suscripción y Términos de Servicio</h1>
        <p className="text-sm text-gray-500">Versión {CONTRACT_VERSION} · vigente desde el {EFFECTIVE_DATE}</p>

        <p className="mt-6">
          Este contrato regula la contratación y el uso de la plataforma <strong>Recontrata</strong>,
          operada por <strong>SALTRONIC SpA</strong>, RUT 78.462.524-9, representada por don Germán
          Saltrón Mellado, con domicilio en Eleuterio Ramírez N° 1199, depto. 84, Parque del Sol,
          comuna de Quilpué, Región de Valparaíso, Chile (en adelante "Saltronic", "el Proveedor" o
          "Recontrata"), y la persona jurídica que se registra y contrata en la plataforma (en
          adelante "el Cliente"). Se perfecciona cuando un representante del Cliente, con facultades
          para obligarlo, <strong>acepta electrónicamente este contrato al registrar su cuenta</strong>,
          aceptación previa a cualquier contratación de un plan de pago. La aceptación electrónica
          tiene el mismo valor que la firma manuscrita conforme a la Ley N° 19.799.
        </p>

        <h2 className="text-xl font-semibold mt-8">1. Definiciones</h2>
        <ul className="list-disc pl-5 space-y-1">
          <li><strong>Plataforma / Servicio:</strong> la aplicación web y móvil "Recontrata" que permite al Cliente registrar y evaluar el desempeño de sus propios trabajadores para apoyar decisiones de recontratación.</li>
          <li><strong>Usuario:</strong> cada persona (supervisor, administrador) que el Cliente autoriza a acceder bajo su cuenta.</li>
          <li><strong>Trabajador Evaluado:</strong> persona natural cuyo desempeño el Cliente registra. No es parte de este contrato, pero es titular de los datos y goza de los derechos de la Cláusula 8.</li>
          <li><strong>Datos del Cliente:</strong> la información que el Cliente carga o genera en la Plataforma.</li>
          <li><strong>Datos Anonimizados:</strong> datos agregados y disociados de forma irreversible, que no permiten identificar a ninguna persona ni empresa.</li>
        </ul>

        <h2 className="text-xl font-semibold mt-8">2. Objeto</h2>
        <p>
          Saltronic otorga al Cliente una licencia de uso no exclusiva, intransferible y limitada a
          la vigencia de este contrato, para usar la Plataforma bajo la modalidad de software como
          servicio (SaaS), conforme al plan contratado. El Cliente no adquiere copia, propiedad ni
          código del software.
        </p>

        <h2 className="text-xl font-semibold mt-8">3. Descripción y alcance del Servicio</h2>
        <p>La Plataforma permite al Cliente, respecto de sus propios trabajadores:</p>
        <ul className="list-disc pl-5 space-y-1">
          <li>Registrar trabajadores y proyectos/faenas.</li>
          <li>Evaluar el desempeño en cinco dimensiones (calidad, seguridad, puntualidad, trabajo en equipo, habilidad técnica) más una recomendación de recontratación.</li>
          <li>Obtener un puntaje calculado mediante una <strong>fórmula ponderada por industria</strong> (no mediante inteligencia artificial), historial y reportes.</li>
          <li>Poner a disposición de cada Trabajador Evaluado un portal de transparencia (Cláusula 8).</li>
        </ul>
        <p className="mt-3">
          <strong>Aislamiento de datos:</strong> cada Cliente accede únicamente a los datos de sus
          propios trabajadores y evaluaciones. La Plataforma <strong>no comparte, cruza ni pone a
          disposición de un Cliente los datos de trabajadores de otro Cliente</strong>. Recontrata no
          es una lista, base de datos ni registro compartido de trabajadores entre empresas. El
          Cliente reconoce que las decisiones de contratación, recontratación o desvinculación son de
          su exclusiva responsabilidad.
        </p>

        <h2 className="text-xl font-semibold mt-8">4. Planes, precios y facturación</h2>
        <ul className="list-disc pl-5 space-y-1">
          <li>Los planes, límites y precios vigentes son los publicados en recontrata.cl al momento de la contratación.</li>
          <li>Los precios publicados son <strong>valores netos en pesos chilenos (CLP)</strong>, a los que se agrega el <strong>IVA</strong> que corresponda conforme a la ley.</li>
          <li>El cobro es por banda de trabajadores activos, según el plan. Los planes de pago incluyen 14 días de prueba gratis.</li>
          <li>La facturación es mensual o anual, mediante la pasarela de pago Flow. El Cliente autoriza el cobro recurrente automático hasta que cancele.</li>
        </ul>

        <h2 className="text-xl font-semibold mt-8">5. Renovación, cancelación y reembolsos</h2>
        <ul className="list-disc pl-5 space-y-1">
          <li>La suscripción se renueva automáticamente por períodos iguales, salvo cancelación.</li>
          <li>El Cliente puede cancelar en cualquier momento desde la Plataforma; la cancelación surte efecto al término del período ya pagado, hasta cuando conserva el acceso.</li>
          <li><strong>No se efectúan reembolsos</strong> por períodos ya pagados ni por uso parcial.</li>
          <li>Si un pago recurrente falla, Saltronic podrá reintentarlo y otorgar un período de gracia de 7 días antes de degradar la cuenta al plan Gratis. El historial no se elimina.</li>
        </ul>

        <h2 className="text-xl font-semibold mt-8">6. Obligaciones del Cliente</h2>
        <p>El Cliente se obliga a:</p>
        <ul className="list-disc pl-5 space-y-1">
          <li>Usar la Plataforma conforme a la ley y a este contrato.</li>
          <li>Mantener la confidencialidad de las credenciales de sus Usuarios y responder por su uso.</li>
          <li><strong>Garantizar que cuenta con base de licitud</strong> para tratar los datos de sus Trabajadores Evaluados, y que las evaluaciones son objetivas, veraces y referidas a desempeño laboral, no a características protegidas ni a represalias.</li>
          <li>Informar a sus trabajadores que su desempeño será evaluado y facilitarles el ejercicio de sus derechos (Cláusula 8).</li>
          <li>No usar la Plataforma para confeccionar listas negras, discriminar arbitrariamente ni para fines contrarios a la normativa laboral o de datos personales.</li>
        </ul>
        <p className="mt-3">El incumplimiento de estas obligaciones es de exclusiva responsabilidad del Cliente, quien mantendrá indemne a Saltronic conforme a la Cláusula 11.</p>

        <h2 className="text-xl font-semibold mt-8">7. Protección de datos personales (Ley N° 21.719)</h2>
        <p>
          <strong>7.1. Roles.</strong> Respecto de los datos de los Trabajadores Evaluados, el
          Cliente actúa como <strong>Responsable</strong> del tratamiento y Saltronic como
          <strong> Encargado</strong> que trata dichos datos por cuenta y según las instrucciones del
          Cliente.
        </p>
        <p>
          <strong>7.2. Base de licitud.</strong> El Cliente declara y garantiza contar con una base
          de licitud válida para tratar los datos de sus trabajadores, y ser quien la determina e
          informa.
        </p>
        <p>
          <strong>7.3. Obligaciones de Saltronic.</strong> Saltronic tratará los datos solo para
          prestar el Servicio; aplicará medidas de seguridad razonables (cifrado en tránsito, control
          de acceso, aislamiento por Cliente); no los cederá salvo a los subencargados necesarios
          (7.5); apoyará al Cliente en la atención de los derechos de los titulares; y eliminará o
          devolverá los datos al término del contrato (Cláusula 13).
        </p>
        <p>
          <strong>7.4. Datos Anonimizados.</strong> Saltronic podrá generar y usar Datos Anonimizados
          (agregados y sin reidentificación posible) para operar, mejorar y desarrollar el Servicio y
          para estadísticas del sector. Por definición no identifican a ninguna persona ni empresa y
          no constituyen datos personales.
        </p>
        <p>
          <strong>7.5. Subencargados.</strong> El Cliente autoriza el uso de proveedores de
          infraestructura para operar el Servicio (actualmente Supabase, Railway, Clerk, Cloudflare y
          Flow). Los datos se alojan en la región Sudamérica cuando el proveedor lo permite.
        </p>
        <p>
          <strong>7.6. Incidentes.</strong> Saltronic notificará al Cliente, sin demora indebida,
          cualquier vulneración de seguridad que afecte sus datos personales.
        </p>

        <h2 className="text-xl font-semibold mt-8">8. Derechos de los Trabajadores Evaluados</h2>
        <p>
          La Plataforma provee, para cada Trabajador Evaluado, un portal de transparencia con enlace
          privado mediante el cual el trabajador puede ver su historial y cómo se calcula su puntaje,
          responder a sus evaluaciones (derecho a réplica) y solicitar dejar de ser evaluado
          (oposición). El portal no revela la identidad de quien evaluó. Estos mecanismos apoyan el
          ejercicio de los derechos reconocidos en la Ley N° 21.719, cuya atención de fondo
          corresponde al Cliente como Responsable, con el apoyo operativo de Saltronic.
        </p>

        <h2 className="text-xl font-semibold mt-8">9. Propiedad intelectual</h2>
        <p>
          La Plataforma, su software, la marca "Recontrata", diseño y documentación son de propiedad
          exclusiva de Saltronic; este contrato solo otorga la licencia de uso de la Cláusula 2. Los
          Datos del Cliente son y seguirán siendo del Cliente; Saltronic solo los trata para prestar el
          Servicio.
        </p>

        <h2 className="text-xl font-semibold mt-8">10. Disponibilidad y niveles de servicio</h2>
        <p>
          El Servicio se presta <strong>"tal cual" y "según disponibilidad"</strong>. Saltronic pondrá
          esfuerzos comerciales razonables para mantener la Plataforma operativa, pero no garantiza un
          porcentaje de disponibilidad (uptime) ni un tiempo de respuesta, ni otorga créditos o
          compensaciones por interrupciones, mantenimientos o fallas de terceros proveedores. Saltronic
          podrá realizar mantenimientos y actualizaciones, procurando avisar los programados con
          antelación razonable.
        </p>

        <h2 className="text-xl font-semibold mt-8">11. Garantías, responsabilidad e indemnidad</h2>
        <p>
          <strong>11.1.</strong> Salvo lo expresamente señalado, Saltronic no otorga garantías de
          idoneidad para un fin particular ni de resultados (por ejemplo, sobre las decisiones de
          recontratación del Cliente).
        </p>
        <p>
          <strong>11.2.</strong> En la máxima medida permitida por la ley, la responsabilidad total de
          Saltronic frente al Cliente se limita al monto efectivamente pagado por el Cliente en los
          últimos 12 meses. Saltronic no responde por daños indirectos, lucro cesante ni pérdida de
          datos imputable a factores fuera de su control razonable.
        </p>
        <p>
          <strong>11.3.</strong> El Cliente mantendrá indemne a Saltronic frente a reclamos de terceros
          (en especial de trabajadores, sindicatos o de la Dirección del Trabajo) derivados del uso que
          el Cliente haga de la Plataforma o del incumplimiento de sus obligaciones (Cláusulas 6 y 7).
        </p>

        <h2 className="text-xl font-semibold mt-8">12. Confidencialidad</h2>
        <p>
          Cada Parte mantendrá reserva sobre la información confidencial de la otra a la que acceda con
          ocasión del contrato, usándola solo para cumplirlo. Esta obligación subsiste por 3 años tras
          el término del contrato. Los Datos del Cliente se rigen, además, por la Cláusula 7.
        </p>

        <h2 className="text-xl font-semibold mt-8">13. Vigencia, término y devolución de datos</h2>
        <p>
          El contrato rige desde su aceptación y mientras exista una suscripción activa. Cualquiera de
          las Partes puede ponerle término según la Cláusula 5 o por incumplimiento grave de la otra no
          subsanado dentro de 10 días de notificado. Al término, Saltronic pondrá los Datos del Cliente
          a su disposición para exportación durante 30 días; transcurrido ese plazo podrá eliminarlos,
          salvo obligación legal de conservarlos. Los Datos Anonimizados no se eliminan por no ser datos
          personales.
        </p>

        <h2 className="text-xl font-semibold mt-8">14. Modificaciones</h2>
        <p>
          Saltronic podrá modificar este contrato y los precios, avisando con al menos 30 días de
          anticipación por correo electrónico o dentro de la Plataforma. Si el Cliente no está de
          acuerdo, podrá cancelar antes de que la modificación entre en vigencia; el uso posterior
          implica aceptación.
        </p>

        <h2 className="text-xl font-semibold mt-8">15. Aceptación electrónica y registro</h2>
        <p>
          El Cliente acepta este contrato marcando la casilla correspondiente al registrar su cuenta,
          aceptación previa a cualquier contratación de un plan de pago. Saltronic registrará la
          aceptación con la identidad del Usuario que acepta, la versión del contrato, la fecha y hora,
          y la dirección IP, como prueba de la manifestación de voluntad (Ley N° 19.799).
        </p>

        <h2 className="text-xl font-semibold mt-8">16. Ley aplicable y jurisdicción</h2>
        <p>
          Este contrato se rige por las leyes de la República de Chile. Cualquier controversia se
          someterá a los tribunales ordinarios de justicia de la comuna de Quilpué, Región de
          Valparaíso.
        </p>

        <h2 className="text-xl font-semibold mt-8">17. Comunicaciones</h2>
        <p>
          Las comunicaciones a Saltronic se dirigirán a{' '}
          <a href="mailto:contacto@recontrata.cl" className="text-blue-600 hover:underline">contacto@recontrata.cl</a>.
          Las comunicaciones al Cliente se dirigirán al correo del administrador registrado en la cuenta.
        </p>

        <p className="mt-8 text-sm text-gray-500">
          SALTRONIC SpA · RUT 78.462.524-9 · Quilpué, Región de Valparaíso · contacto@recontrata.cl
        </p>
      </article>
    </div>
  )
}
