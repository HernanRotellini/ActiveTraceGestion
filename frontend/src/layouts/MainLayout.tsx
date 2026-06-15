import { useState } from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { useSession } from '@/shared/hooks/useSession'
import { useLogout } from '@/features/auth/hooks/useLogout'
import { Button } from '@/shared/components/Button'

interface MenuItem {
  label: string
  route: string
  requiredPermission?: string
  group?: 'educativo' | 'facturacion' | 'auditoria'
}

const menuItems: MenuItem[] = [
  { label: 'Inicio', route: '/' },
  { label: 'Carreras', route: '/admin/estructura/carreras', requiredPermission: 'estructura:gestionar', group: 'educativo' },
  { label: 'Cohortes', route: '/admin/estructura/cohortes', requiredPermission: 'estructura:gestionar', group: 'educativo' },
  { label: 'Materias', route: '/admin/estructura/materias', requiredPermission: 'estructura:gestionar', group: 'educativo' },
  { label: 'Setup cuatrimestre', route: '/coordinacion/setup-cuatrimestre', requiredPermission: 'periodos:gestionar', group: 'educativo' },
  { label: 'Mis Comisiones', route: '/docente/comisiones', requiredPermission: 'calificaciones:ver', group: 'educativo' },
  { label: 'Entregas sin corregir', route: '/docente/entregas', requiredPermission: 'atrasados:ver', group: 'educativo' },
  { label: 'Comunicaciones', route: '/docente/comunicaciones', requiredPermission: 'comunicacion:enviar', group: 'educativo' },
  { label: 'Monitor', route: '/docente/monitor', requiredPermission: 'atrasados:ver', group: 'educativo' },
  { label: 'Equipos docentes', route: '/coordinacion/equipos-docentes', requiredPermission: 'equipos:ver', group: 'educativo' },
  { label: 'Avisos', route: '/coordinacion/avisos', requiredPermission: 'avisos:ver', group: 'educativo' },
  { label: 'Tareas internas', route: '/coordinacion/tareas', requiredPermission: 'tareas:ver', group: 'educativo' },
  { label: 'Encuentros', route: '/coordinacion/encuentros', requiredPermission: 'encuentros:ver', group: 'educativo' },
  { label: 'Coloquios', route: '/coordinacion/coloquios', requiredPermission: 'coloquios:ver', group: 'educativo' },
  { label: 'Monitor general', route: '/coordinacion/monitores', requiredPermission: 'atrasados:ver', group: 'educativo' },
  { label: 'Usuarios', route: '/admin/usuarios', requiredPermission: 'usuarios:gestionar', group: 'educativo' },
  { label: 'Liquidaciones', route: '/liquidaciones', requiredPermission: 'liquidaciones:ver', group: 'facturacion' },
  { label: 'Grilla salarial', route: '/liquidaciones/grilla-salarial', requiredPermission: 'liquidaciones:gestionar', group: 'facturacion' },
  { label: 'Facturas', route: '/liquidaciones/facturas', requiredPermission: 'liquidaciones:ver', group: 'facturacion' },
  { label: 'Auditoría', route: '/admin/auditoria', requiredPermission: 'auditoria:ver', group: 'auditoria' },
  { label: 'Log auditoría', route: '/admin/auditoria/log', requiredPermission: 'auditoria:ver', group: 'auditoria' },
]

const sectionHeaders: { label: string; group: 'educativo' | 'facturacion' | 'auditoria' }[] = [
  { label: 'EDUCATIVO', group: 'educativo' },
  { label: 'FACTURACIÓN Y SALARIOS', group: 'facturacion' },
  { label: 'AUDITORÍA', group: 'auditoria' },
]

interface SidebarHeader {
  kind: 'header'
  label: string
  group: string
}

function buildSidebarSections(items: MenuItem[]): (MenuItem | SidebarHeader)[] {
  const result: (MenuItem | SidebarHeader)[] = []

  const standalone = items.filter(item => !item.group)
  result.push(...standalone)

  const groupsWithItems = new Set(items.filter(item => item.group).map(item => item.group!))

  for (const section of sectionHeaders) {
    if (!groupsWithItems.has(section.group)) continue
    result.push({ kind: 'header', label: section.label, group: section.group })
    const groupItems = items.filter(item => item.group === section.group)
    result.push(...groupItems)
  }

  return result
}

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
            {buildSidebarSections(visibleItems).map((item) => {
              if ('kind' in item && item.kind === 'header') {
                return (
                  <li key={`header-${item.group}`}>
                    <div
                      className="border-t border-gray-100 px-4 py-1.5 pt-3 mt-4"
                      aria-hidden="true"
                    >
                      <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                        {item.label}
                      </span>
                    </div>
                  </li>
                )
              }
              const menuItem = item as MenuItem
              return (
                <li key={menuItem.route}>
                  <NavLink
                    to={menuItem.route}
                    end={menuItem.route === '/'}
                    className={({ isActive }) =>
                      `block rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-primary-50 text-primary-700'
                          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                      }`
                    }
                    onClick={() => setSidebarOpen(false)}
                  >
                    {menuItem.label}
                  </NavLink>
                </li>
              )
            })}
          </ul>
        </nav>

        {session?.user && (
          <div className="border-t p-4">
            <p className="text-sm font-medium text-gray-900 truncate">
              {session.user.nombre && session.user.apellidos
                ? `${session.user.nombre} ${session.user.apellidos}`
                : (session.user.email ?? session.user.user_id)}
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
