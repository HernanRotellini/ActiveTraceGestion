import { createBrowserRouter } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { AuthGuard } from '@/guards/AuthGuard'
import { PermissionGuard } from '@/guards/PermissionGuard'

const LoginPage = lazy(() => import('@/features/auth/pages/LoginPage'))
const Challenge2faPage = lazy(() => import('@/features/auth/pages/Challenge2faPage'))
const RecoveryPage = lazy(() => import('@/features/auth/pages/RecoveryPage'))
const ResetPasswordPage = lazy(() => import('@/features/auth/pages/ResetPasswordPage'))
const MainLayout = lazy(() => import('@/layouts/MainLayout'))
const ForbiddenPage = lazy(() => import('@/pages/ForbiddenPage'))
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'))

const ComisionesListPage = lazy(() => import('@/features/comisiones/pages/ComisionesListPage'))
const ComisionDetailPage = lazy(() => import('@/features/comisiones/pages/ComisionDetailPage'))
const EntregasPendientesPage = lazy(() => import('@/features/entregas-sin-corregir/pages/EntregasPendientesPage'))
const ComunicacionesPage = lazy(() => import('@/features/comunicaciones/pages/ComunicacionesPage'))
const MonitorPage = lazy(() => import('@/features/monitores/pages/MonitorPage'))
const MonitorGeneralPage = lazy(() => import('@/features/monitores/pages/MonitorGeneralPage'))
const EquiposListPage = lazy(() => import('@/features/equipos-docentes/pages/EquiposListPage'))
const EquipoDetailPage = lazy(() => import('@/features/equipos-docentes/pages/EquipoDetailPage'))
const EquipoFormPage = lazy(() => import('@/features/equipos-docentes/pages/EquipoFormPage'))
const AvisosListPage = lazy(() => import('@/features/avisos/pages/AvisosListPage'))
const AvisoFormPage = lazy(() => import('@/features/avisos/pages/AvisoFormPage'))
const AvisoDetailPage = lazy(() => import('@/features/avisos/pages/AvisoDetailPage'))
const TareasListPage = lazy(() => import('@/features/tareas-internas/pages/TareasListPage'))
const TareaDetailPage = lazy(() => import('@/features/tareas-internas/pages/TareaDetailPage'))
const TareaFormPage = lazy(() => import('@/features/tareas-internas/pages/TareaFormPage'))
const EncuentrosListPage = lazy(() => import('@/features/encuentros/pages/EncuentrosListPage'))
const EncuentroDetailPage = lazy(() => import('@/features/encuentros/pages/EncuentroDetailPage'))
const ColoquiosListPage = lazy(() => import('@/features/coloquios/pages/ColoquiosListPage'))
const ColoquioDetailPage = lazy(() => import('@/features/coloquios/pages/ColoquioDetailPage'))
const SetupCuatrimestrePage = lazy(() => import('@/features/setup-cuatrimestre/pages/SetupCuatrimestrePage'))
const LiquidacionPeriodoPage = lazy(() => import('@/features/liquidaciones/pages/LiquidacionPeriodoPage'))
const LiquidacionHistorialPage = lazy(() => import('@/features/liquidaciones/pages/LiquidacionHistorialPage'))
const GrillaSalarialPage = lazy(() => import('@/features/liquidaciones/pages/GrillaSalarialPage'))
const FacturasPage = lazy(() => import('@/features/liquidaciones/pages/FacturasPage'))
const CarrerasPage = lazy(() => import('@/features/admin/pages/CarrerasPage'))
const CohortesPage = lazy(() => import('@/features/admin/pages/CohortesPage'))
const MateriasPage = lazy(() => import('@/features/admin/pages/MateriasPage'))
const UsuariosPage = lazy(() => import('@/features/admin/pages/UsuariosPage'))
const AuditoriaDashboardPage = lazy(() => import('@/features/admin/pages/AuditoriaDashboardPage'))
const AuditoriaLogPage = lazy(() => import('@/features/admin/pages/AuditoriaLogPage'))

function LazyFallback() {
  return (
    <div className="flex h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-300 border-t-primary-600" />
    </div>
  )
}

function SuspenseWrapper({ Component }: { Component: React.LazyExoticComponent<React.ComponentType> }) {
  return (
    <Suspense fallback={<LazyFallback />}>
      <Component />
    </Suspense>
  )
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <SuspenseWrapper Component={LoginPage} />,
  },
  {
    path: '/auth/2fa',
    element: <SuspenseWrapper Component={Challenge2faPage} />,
  },
  {
    path: '/auth/recuperar',
    element: <SuspenseWrapper Component={RecoveryPage} />,
  },
  {
    path: '/auth/restablecer',
    element: <SuspenseWrapper Component={ResetPasswordPage} />,
  },
  {
    path: '/403',
    element: <SuspenseWrapper Component={ForbiddenPage} />,
  },
  {
    path: '/404',
    element: <SuspenseWrapper Component={NotFoundPage} />,
  },
  {
    path: '/',
    element: <AuthGuard />,
    children: [
      {
        element: <SuspenseWrapper Component={MainLayout} />,
        children: [
          {
            index: true,
        element: (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <h2 className="text-xl font-semibold text-gray-700">Bienvenido a Trace</h2>
                <p className="mt-2 text-gray-500">Seleccione una sección del menú lateral.</p>
              </div>
            </div>
          ),
          },
          {
            path: 'docente/comisiones',
            element: (
              <PermissionGuard requiredPermissions={['calificaciones:ver']}>
                <SuspenseWrapper Component={ComisionesListPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'docente/comisiones/:id',
            element: (
              <PermissionGuard requiredPermissions={['calificaciones:ver']}>
                <SuspenseWrapper Component={ComisionDetailPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'docente/entregas',
            element: (
              <PermissionGuard requiredPermissions={['atrasados:ver']}>
                <SuspenseWrapper Component={EntregasPendientesPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'docente/comunicaciones',
            element: (
              <PermissionGuard requiredPermissions={['comunicacion:enviar']}>
                <SuspenseWrapper Component={ComunicacionesPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'docente/monitor',
            element: (
              <PermissionGuard requiredPermissions={['atrasados:ver']}>
                <SuspenseWrapper Component={MonitorPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/equipos-docentes',
            element: (
              <PermissionGuard requiredPermissions={['equipos:ver']}>
                <SuspenseWrapper Component={EquiposListPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/equipos-docentes/nuevo',
            element: (
              <PermissionGuard requiredPermissions={['equipos:gestionar']}>
                <SuspenseWrapper Component={EquipoFormPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/equipos-docentes/:id',
            element: (
              <PermissionGuard requiredPermissions={['equipos:ver']}>
                <SuspenseWrapper Component={EquipoDetailPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/equipos-docentes/:id/editar',
            element: (
              <PermissionGuard requiredPermissions={['equipos:gestionar']}>
                <SuspenseWrapper Component={EquipoFormPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/avisos',
            element: (
              <PermissionGuard requiredPermissions={['avisos:ver']}>
                <SuspenseWrapper Component={AvisosListPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/avisos/nuevo',
            element: (
              <PermissionGuard requiredPermissions={['avisos:gestionar']}>
                <SuspenseWrapper Component={AvisoFormPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/avisos/:id',
            element: (
              <PermissionGuard requiredPermissions={['avisos:ver']}>
                <SuspenseWrapper Component={AvisoDetailPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/avisos/:id/editar',
            element: (
              <PermissionGuard requiredPermissions={['avisos:gestionar']}>
                <SuspenseWrapper Component={AvisoFormPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/tareas',
            element: (
              <PermissionGuard requiredPermissions={['tareas:ver']}>
                <SuspenseWrapper Component={TareasListPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/tareas/nuevo',
            element: (
              <PermissionGuard requiredPermissions={['tareas:gestionar']}>
                <SuspenseWrapper Component={TareaFormPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/tareas/:id',
            element: (
              <PermissionGuard requiredPermissions={['tareas:ver']}>
                <SuspenseWrapper Component={TareaDetailPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/tareas/:id/editar',
            element: (
              <PermissionGuard requiredPermissions={['tareas:gestionar']}>
                <SuspenseWrapper Component={TareaFormPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/encuentros',
            element: (
              <PermissionGuard requiredPermissions={['encuentros:ver']}>
                <SuspenseWrapper Component={EncuentrosListPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/encuentros/:id',
            element: (
              <PermissionGuard requiredPermissions={['encuentros:ver']}>
                <SuspenseWrapper Component={EncuentroDetailPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/coloquios',
            element: (
              <PermissionGuard requiredPermissions={['coloquios:ver']}>
                <SuspenseWrapper Component={ColoquiosListPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/coloquios/:id',
            element: (
              <PermissionGuard requiredPermissions={['coloquios:ver']}>
                <SuspenseWrapper Component={ColoquioDetailPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/setup-cuatrimestre',
            element: (
              <PermissionGuard requiredPermissions={['estructura:gestionar']}>
                <SuspenseWrapper Component={SetupCuatrimestrePage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'coordinacion/monitores',
            element: (
              <PermissionGuard requiredPermissions={['atrasados:ver']}>
                <SuspenseWrapper Component={MonitorGeneralPage} />
              </PermissionGuard>
            ),
          },
          // FINANZAS
          {
            path: 'liquidaciones',
            element: (
              <PermissionGuard requiredPermissions={['liquidaciones:ver']}>
                <SuspenseWrapper Component={LiquidacionPeriodoPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'liquidaciones/historial',
            element: (
              <PermissionGuard requiredPermissions={['liquidaciones:ver']}>
                <SuspenseWrapper Component={LiquidacionHistorialPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'liquidaciones/grilla-salarial',
            element: (
              <PermissionGuard requiredPermissions={['liquidaciones:gestionar']}>
                <SuspenseWrapper Component={GrillaSalarialPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'liquidaciones/facturas',
            element: (
              <PermissionGuard requiredPermissions={['liquidaciones:ver']}>
                <SuspenseWrapper Component={FacturasPage} />
              </PermissionGuard>
            ),
          },
          // ADMIN — Estructura
          {
            path: 'admin/estructura/carreras',
            element: (
              <PermissionGuard requiredPermissions={['estructura:gestionar']}>
                <SuspenseWrapper Component={CarrerasPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'admin/estructura/cohortes',
            element: (
              <PermissionGuard requiredPermissions={['estructura:gestionar']}>
                <SuspenseWrapper Component={CohortesPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'admin/estructura/materias',
            element: (
              <PermissionGuard requiredPermissions={['estructura:gestionar']}>
                <SuspenseWrapper Component={MateriasPage} />
              </PermissionGuard>
            ),
          },
          // ADMIN — Usuarios
          {
            path: 'admin/usuarios',
            element: (
              <PermissionGuard requiredPermissions={['usuarios:gestionar']}>
                <SuspenseWrapper Component={UsuariosPage} />
              </PermissionGuard>
            ),
          },
          // ADMIN — Auditoría
          {
            path: 'admin/auditoria',
            element: (
              <PermissionGuard requiredPermissions={['auditoria:ver']}>
                <SuspenseWrapper Component={AuditoriaDashboardPage} />
              </PermissionGuard>
            ),
          },
          {
            path: 'admin/auditoria/log',
            element: (
              <PermissionGuard requiredPermissions={['auditoria:ver']}>
                <SuspenseWrapper Component={AuditoriaLogPage} />
              </PermissionGuard>
            ),
          },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <SuspenseWrapper Component={NotFoundPage} />,
  },
])
