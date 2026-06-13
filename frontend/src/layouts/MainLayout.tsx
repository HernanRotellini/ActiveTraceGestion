import { useState } from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { useSession } from '@/shared/hooks/useSession'
import { useLogout } from '@/features/auth/hooks/useLogout'
import { Button } from '@/shared/components/Button'

interface MenuItem {
  label: string
  route: string
  requiredPermission?: string
}

const menuItems: MenuItem[] = [
  { label: 'Inicio', route: '/' },
  { label: 'Mis Comisiones', route: '/docente/comisiones', requiredPermission: 'calificaciones:ver' },
  { label: 'Entregas sin corregir', route: '/docente/entregas', requiredPermission: 'atrasados:ver' },
  { label: 'Comunicaciones', route: '/docente/comunicaciones', requiredPermission: 'comunicacion:enviar' },
  { label: 'Monitor', route: '/docente/monitor', requiredPermission: 'atrasados:ver' },
  { label: 'Equipos docentes', route: '/coordinacion/equipos-docentes', requiredPermission: 'equipos:ver' },
  { label: 'Avisos', route: '/coordinacion/avisos', requiredPermission: 'avisos:ver' },
  { label: 'Tareas internas', route: '/coordinacion/tareas', requiredPermission: 'tareas:ver' },
  { label: 'Encuentros', route: '/coordinacion/encuentros', requiredPermission: 'encuentros:ver' },
  { label: 'Coloquios', route: '/coordinacion/coloquios', requiredPermission: 'coloquios:ver' },
  { label: 'Setup cuatrimestre', route: '/coordinacion/setup-cuatrimestre', requiredPermission: 'estructura:gestionar' },
  { label: 'Monitor general', route: '/coordinacion/monitores', requiredPermission: 'atrasados:ver' },
  { label: 'Liquidaciones', route: '/liquidaciones', requiredPermission: 'liquidaciones:ver' },
  { label: 'Grilla salarial', route: '/liquidaciones/grilla-salarial', requiredPermission: 'liquidaciones:gestionar' },
  { label: 'Facturas', route: '/liquidaciones/facturas', requiredPermission: 'liquidaciones:ver' },
  { label: 'Carreras', route: '/admin/estructura/carreras', requiredPermission: 'estructura:gestionar' },
  { label: 'Cohortes', route: '/admin/estructura/cohortes', requiredPermission: 'estructura:gestionar' },
  { label: 'Materias', route: '/admin/estructura/materias', requiredPermission: 'estructura:gestionar' },
  { label: 'Usuarios', route: '/admin/usuarios', requiredPermission: 'usuarios:gestionar' },
  { label: 'Auditoría', route: '/admin/auditoria', requiredPermission: 'auditoria:ver' },
  { label: 'Log auditoría', route: '/admin/auditoria/log', requiredPermission: 'auditoria:ver' },
]

export default function MainLayout() {
  const { session, hasPermission } = useSession()
  const { logout, isLoading: isLoggingOut } = useLogout()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const visibleItems = menuItems.filter(
    (item) => !item.requiredPermission || hasPermission(item.requiredPermission),
  )

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <div
        className={`fixed inset-0 z-20 bg-black/50 transition-opacity lg:hidden ${
          sidebarOpen ? 'opacity-100' : 'pointer-events-none opacity-0'
        }`}
        onClick={() => setSidebarOpen(false)}
      />

      <aside
        className={`fixed inset-y-0 left-0 z-30 flex w-64 flex-col bg-white shadow-lg transition-transform lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-16 items-center justify-between border-b px-6">
          <span className="text-lg font-bold text-primary-600">Trace</span>
          <button
            className="text-gray-500 hover:text-gray-700 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto p-4">
          <ul className="space-y-1">
            {visibleItems.map((item) => (
              <li key={item.route}>
                <NavLink
                  to={item.route}
                  end={item.route === '/'}
                  className={({ isActive }) =>
                    `block rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`
                  }
                  onClick={() => setSidebarOpen(false)}
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {session?.user && (
          <div className="border-t p-4">
            <p className="text-sm font-medium text-gray-900 truncate">
              {session.user.email ?? session.user.user_id}
            </p>
            <p className="text-xs text-gray-500 truncate">
              {session.user.roles?.join(', ')}
            </p>
          </div>
        )}
      </aside>

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-16 items-center justify-between border-b bg-white px-6">
          <button
            className="text-gray-500 hover:text-gray-700 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div className="flex-1" />

          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={logout} loading={isLoggingOut}>
              Cerrar sesión
            </Button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
