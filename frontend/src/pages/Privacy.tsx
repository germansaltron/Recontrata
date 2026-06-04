import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'

export default function Privacy() {
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
        <h1 className="text-3xl font-bold text-gray-900">Política de Privacidad</h1>
        <p className="text-sm text-gray-500">Última actualización: 4 de junio de 2026</p>

        <p className="mt-6">
          Esta Política describe cómo Recontrata ("nosotros") trata los datos personales
          que los usuarios del Servicio ("Usuario") ingresan o generan al usar la plataforma.
          Respetamos la Ley N° 21.719, que regula la protección y el tratamiento de los datos
          personales y moderniza la Ley N° 19.628, y, para usuarios de la Unión Europea, el
          Reglamento General de Protección de Datos (RGPD) en lo que sea aplicable.
        </p>

        <h2 className="text-xl font-semibold mt-8">1. Responsable del tratamiento</h2>
        <p>
          El Usuario (empresa contratista) es el responsable del tratamiento de los datos de
          trabajadores que carga en la plataforma. Recontrata actúa como encargado de dichos
          datos, en los términos que establece la Ley N° 21.719.
        </p>
        <p>
          Respecto de los datos del propio Usuario (nombre, correo electrónico, datos de
          organización, datos de pago) Recontrata actúa como responsable.
        </p>

        <h2 className="text-xl font-semibold mt-8">2. Datos que tratamos</h2>
        <ul className="list-disc pl-5 space-y-1">
          <li><strong>Datos de cuenta del Usuario:</strong> nombre, correo, organización, fecha de creación.</li>
          <li><strong>Datos de trabajadores cargados por el Usuario:</strong> nombres, RUT, especialidad, teléfono, email, asignación a proyectos, evaluaciones (puntajes, comentarios, recomendación de recontratación).</li>
          <li><strong>Datos técnicos:</strong> logs de actividad, dirección IP, tipo de navegador, eventos de uso anonimizados.</li>
          <li><strong>Datos de pago:</strong> son procesados por proveedores terceros (pasarelas de pago); no almacenamos números completos de tarjetas.</li>
        </ul>

        <h2 className="text-xl font-semibold mt-8">3. Finalidades del tratamiento</h2>
        <ul className="list-disc pl-5 space-y-1">
          <li>Prestar el Servicio contratado por el Usuario.</li>
          <li>Facturar y cobrar los planes contratados.</li>
          <li>Soporte y comunicaciones operacionales sobre el Servicio.</li>
          <li>Mejorar la plataforma utilizando datos agregados y anonimizados.</li>
          <li>Cumplir obligaciones legales o requerimientos de autoridad competente.</li>
        </ul>

        <h2 className="text-xl font-semibold mt-8">4. Base de licitud</h2>
        <p>
          Tratamos datos del Usuario sobre la base del contrato (estos Términos) y del
          consentimiento al registrarse. El tratamiento de datos de los trabajadores recae en
          el Usuario, quien declara contar con base legal para dicho tratamiento (interés
          legítimo, relación laboral, consentimiento informado u otra aplicable).
        </p>

        <h2 className="text-xl font-semibold mt-8">5. Subencargados y terceros</h2>
        <p>
          Para prestar el Servicio nos apoyamos en proveedores que podrían acceder a los
          datos en calidad de subencargados:
        </p>
        <ul className="list-disc pl-5 space-y-1">
          <li><strong>Clerk</strong> — autenticación de usuarios.</li>
          <li><strong>Supabase</strong> — base de datos PostgreSQL (región Sudamérica).</li>
          <li><strong>Railway</strong> — hospedaje de la aplicación.</li>
          <li><strong>Proveedor de pagos</strong> — procesamiento de transacciones (cuando aplique).</li>
        </ul>
        <p>
          Estos proveedores están obligados contractualmente a tratar los datos con niveles de
          seguridad equivalentes o superiores a los nuestros.
        </p>

        <h2 className="text-xl font-semibold mt-8">6. Almacenamiento y transferencia internacional</h2>
        <p>
          Los datos se almacenan principalmente en servidores ubicados en Sudamérica. Algunos
          proveedores pueden replicar datos en otras jurisdicciones. Exigimos a dichos
          proveedores contar con medidas de seguridad apropiadas.
        </p>

        <h2 className="text-xl font-semibold mt-8">7. Plazo de conservación</h2>
        <p>
          Mantenemos los datos mientras la cuenta esté activa. Al cerrar la cuenta,
          eliminaremos los datos en un plazo razonable (máximo 90 días), salvo aquellos que
          debamos conservar por obligación legal o por razones de seguridad y auditoría.
        </p>

        <h2 className="text-xl font-semibold mt-8">8. Derechos de los titulares</h2>
        <p>
          Los titulares de datos personales pueden ejercer los derechos de acceso,
          rectificación, supresión (cancelación), oposición y portabilidad reconocidos en la
          Ley N° 21.719, enviando un correo a{' '}
          <a href="mailto:contacto@recontrata.cl" className="text-blue-600 hover:underline">
            contacto@recontrata.cl
          </a>
          . Si el titular es un trabajador cuyos datos fueron cargados por un contratista,
          recomendamos dirigir la solicitud a dicho contratista (responsable del tratamiento);
          de todos modos, apoyaremos la gestión.
        </p>

        <h2 className="text-xl font-semibold mt-8">9. Seguridad</h2>
        <ul className="list-disc pl-5 space-y-1">
          <li>Cifrado en tránsito (HTTPS/TLS) para todas las comunicaciones.</li>
          <li>Aislamiento multi-tenant: cada organización solo ve sus datos.</li>
          <li>Autenticación robusta provista por Clerk.</li>
          <li>Registros de acceso y auditoría.</li>
        </ul>
        <p>
          Ningún sistema es invulnerable. En caso de incidente de seguridad que afecte datos
          personales, lo notificaremos sin demora injustificada.
        </p>

        <h2 className="text-xl font-semibold mt-8">10. Cookies</h2>
        <p>
          Usamos cookies y tecnologías equivalentes para mantener la sesión iniciada y para
          funcionalidad básica. No utilizamos cookies publicitarias de terceros.
        </p>

        <h2 className="text-xl font-semibold mt-8">11. Cambios a esta Política</h2>
        <p>
          Podremos actualizar esta Política. Los cambios relevantes serán informados por
          email o dentro del Servicio.
        </p>

        <h2 className="text-xl font-semibold mt-8">12. Contacto</h2>
        <p>
          Escribanos a{' '}
          <a href="mailto:contacto@recontrata.cl" className="text-blue-600 hover:underline">
            contacto@recontrata.cl
          </a>{' '}
          para ejercer derechos o resolver dudas sobre esta Política.
        </p>
      </article>
    </div>
  )
}
