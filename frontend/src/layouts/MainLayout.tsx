import { useState } from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { useSession } from '@/shared/hooks/useSession'
import { useLogout } from '@/features/auth/hooks/useLogout'
import { Button } from '@/shared/components/Button'

type SidebarGroup = 'educativo' | 'facturacion' | 'auditoria'

interface MenuItem {
  label: string
  route: string
  requiredPermission?: string
  group?: SidebarGroup
}

const menuItems: MenuItem[] = [
  { label: 'Inicio', route: '/' },
  { label: 'Carreras', route: '/admin/estructura/carreras', requiredPermission: 'estructura:gestionar', group: 'educativo' },
  { label: 'Cohortes', route: '/admin/estructura/cohortes', requiredPermission: 'estructura:gestionar', group: 'educativo' },
  { label: 'Materias', route: '/admin/estructura/materias', requiredPermission: 'estructura:gestionar', group: 'educativo' },
  { label: 'Setup cuatrimestre', route: '/coordinacion/setup-cuatrimestre', requiredPermission: 'estructura:gestionar', group: 'educativo' },
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
  { label: 'Auditoria', route: '/admin/auditoria', requiredPermission: 'auditoria:ver', group: 'auditoria' },
  { label: 'Log auditoria', route: '/admin/auditoria/log', requiredPermission: 'auditoria:ver', group: 'auditoria' },
]

const sectionHeaders: Array<{ label: string; group: SidebarGroup }> = [
  { label: 'Educativo', group: 'educativo' },
  { label: 'Facturacion y salarios', group: 'facturacion' },
  { label: 'Auditoria', group: 'auditoria' },
]

const initialCollapsedSections: Record<SidebarGroup, boolean> = {
  educativo: false,
  facturacion: false,
  auditoria: false,
}

function renderMenuLink(item: MenuItem, onNavigate: () => void) {
  return (
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
        onClick={onNavigate}
      >
        {item.label}
      </NavLink>
    </li>
  )
}

export default function MainLayout() {
  const { session, hasPermission } = useSession()
  const { logout, isLoading: isLoggingOut } = useLogout()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [collapsedSections, setCollapsedSections] = useState(initialCollapsedSections)

  const visibleItems = menuItems.filter(
    (item) => !item.requiredPermission || hasPermission(item.requiredPermission),
  )
  const standaloneItems = visibleItems.filter((item) => !item.group)
  const groupedSections = sectionHeaders
    .map((section) => ({
      ...section,
      items: visibleItems.filter((item) => item.group === section.group),
    }))
    .filter((section) => section.items.length > 0)

  const closeSidebar = () => setSidebarOpen(false)
  const toggleSection = (group: SidebarGroup) => {
    setCollapsedSections((current) => ({
      ...current,
      [group]: !current[group],
    }))
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <div
        className={`fixed inset-0 z-20 bg-black/50 transition-opacity lg:hidden ${
          sidebarOpen ? 'opacity-100' : 'pointer-events-none opacity-0'
        }`}
        onClick={closeSidebar}
      />

      <aside
        className={`fixed inset-y-0 left-0 z-30 flex w-64 flex-col bg-white shadow-lg transition-transform lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-16 items-center justify-between border-b px-6">
          <span className="text-lg font-bold text-primary-600">Trace</span>
          <button
            type="button"
            className="text-gray-500 hover:text-gray-700 lg:hidden"
            onClick={closeSidebar}
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto p-4">
          <ul className="space-y-1">
            {standaloneItems.map((item) => renderMenuLink(item, closeSidebar))}

            {groupedSections.map((section) => {
              const isCollapsed = collapsedSections[section.group]
              return (
                <li key={section.group} className="mt-4">
                  <button
                    type="button"
                    className="flex w-full items-center justify-between border-t border-gray-100 px-4 py-2 pt-3 text-left"
                    onClick={() => toggleSection(section.group)}
                    aria-expanded={!isCollapsed}
                    aria-controls={`sidebar-section-${section.group}`}
                  >
                    <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                      {section.label}
                    </span>
                    <svg
                      className={`h-4 w-4 text-gray-400 transition-transform ${isCollapsed ? '' : 'rotate-90'}`}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>

                  {!isCollapsed && (
                    <ul id={`sidebar-section-${section.group}`} className="mt-1 space-y-1">
                      {section.items.map((item) => renderMenuLink(item, closeSidebar))}
                    </ul>
                  )}
                </li>
              )
            })}
          </ul>
        </nav>

        {session?.user && (
          <div className="border-t p-4">
            <p className="truncate text-sm font-medium text-gray-900">
              {session.user.nombre && session.user.apellidos
                ? `${session.user.nombre} ${session.user.apellidos}`
                : (session.user.email ?? session.user.user_id)}
            </p>
            <p className="truncate text-xs text-gray-500">
              {session.user.roles?.join(', ')}
            </p>
          </div>
        )}
      </aside>

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-16 items-center justify-between border-b bg-white px-6">
          <button
            type="button"
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
              Cerrar sesion
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
