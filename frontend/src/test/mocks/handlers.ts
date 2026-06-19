import { http, HttpResponse } from 'msw'

interface LoginBody {
  tenant_code: string
  email: string
  password: string
}

interface ChallengeBody {
  challenge_id: string
  code: string
}

interface RefreshBody {
  refresh_token: string
}

interface ResetBody {
  token: string
  new_password: string
}

export const handlers = [
  http.post('/api/auth/login', async ({ request }) => {
    const body = await request.json() as LoginBody

    if (body.email === '2fa@test.com') {
      return HttpResponse.json(
        { requires_2fa: true, challenge_id: 'challenge-123' },
        { status: 202 },
      )
    }

    if (body.email === 'user@test.com' && body.password === 'correct') {
      return HttpResponse.json({
        access_token: 'access-token-123',
        refresh_token: 'refresh-token-123',
        token_type: 'bearer',
      })
    }

    if (body.email === 'ratelimit@test.com') {
      return HttpResponse.json(
        { detail: 'Too many requests' },
        { status: 429 },
      )
    }

    return HttpResponse.json(
      { detail: 'Invalid credentials' },
      { status: 401 },
    )
  }),

  http.post('/api/auth/2fa/challenge', async ({ request }) => {
    const body = await request.json() as ChallengeBody

    if (body.code === '123456') {
      return HttpResponse.json({
        access_token: 'access-token-2fa',
        refresh_token: 'refresh-token-2fa',
        token_type: 'bearer',
      })
    }

    return HttpResponse.json(
      { detail: 'Invalid code' },
      { status: 401 },
    )
  }),

  http.post('/api/auth/refresh', async ({ request }) => {
    const body = await request.json() as RefreshBody

    if (body.refresh_token === 'valid-refresh-token') {
      return HttpResponse.json({
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token',
        token_type: 'bearer',
      })
    }

    return HttpResponse.json(
      { detail: 'Invalid refresh token' },
      { status: 401 },
    )
  }),

  http.post('/api/auth/logout', () => {
    return HttpResponse.json(null, { status: 204 })
  }),

  http.post('/api/auth/forgot', () => {
    return HttpResponse.json(
      { message: 'Si el email existe, recibirá instrucciones.' },
      { status: 202 },
    )
  }),

  http.post('/api/auth/reset', async ({ request }) => {
    const body = await request.json() as ResetBody

    if (body.token === 'expired-token') {
      return HttpResponse.json(
        { detail: 'Token inválido o expirado' },
        { status: 401 },
      )
    }

    return HttpResponse.json(null, { status: 204 })
  }),

  http.get('/api/auth/me', () => {
    return HttpResponse.json({
      user_id: 'user-123',
      tenant_id: 'tenant-123',
      roles: ['admin'],
      permissions: ['calificaciones:ver', 'atrasados:ver', 'comunicacion:enviar'],
    })
  }),

  // Calificaciones
  http.post('/api/calificaciones/:comisionId/importar', () => {
    return HttpResponse.json({
      actividades: [
        { actividad_id: 'act-1', nombre: 'Parcial 1', tipo: 'examen', fecha: '2026-05-01', calificaciones_count: 25, seleccionada: true },
        { actividad_id: 'act-2', nombre: 'TP 1', tipo: 'trabajo', fecha: '2026-05-10', calificaciones_count: 22, seleccionada: true },
      ],
    })
  }),

  http.post('/api/calificaciones/:comisionId/confirmar', () => {
    return HttpResponse.json({ count: 2 })
  }),

  http.get('/api/calificaciones/:comisionId', () => {
    return HttpResponse.json([
      { id: 'c-1', alumno_id: 'a-1', alumno_nombre: 'Juan Perez', materia: 'Matemática', nota: 85, estado: 'aprobado', fecha_importacion: '2026-05-01' },
      { id: 'c-2', alumno_id: 'a-2', alumno_nombre: 'Maria Gomez', materia: 'Matemática', nota: 45, estado: 'desaprobado', fecha_importacion: '2026-05-01' },
    ])
  }),

  http.get('/api/calificaciones/:comisionId/atrasados', () => {
    return HttpResponse.json({
      total: 1,
      items: [
        { alumno_id: 'a-3', alumno_nombre: 'Carlos Lopez', materia: 'Matemática', atraso_dias: 20, ultima_actividad: '2026-04-15' },
      ],
    })
  }),

  http.get('/api/calificaciones/:comisionId/ranking', () => {
    return HttpResponse.json([
      { alumno_id: 'a-1', alumno_nombre: 'Juan Perez', promedio: 85.5, puesto: 1, total_actividades: 10 },
      { alumno_id: 'a-2', alumno_nombre: 'Maria Gomez', promedio: 72.0, puesto: 2, total_actividades: 10 },
    ])
  }),

  http.get('/api/calificaciones/:comisionId/notas-finales', () => {
    return HttpResponse.json([
      { alumno_id: 'a-1', alumno_nombre: 'Juan Perez', nota_final: 85, condicion: 'promocionado' },
      { alumno_id: 'a-3', alumno_nombre: 'Carlos Lopez', nota_final: 60, condicion: 'regular' },
    ])
  }),

  http.get('/api/calificaciones/:comisionId/umbral', () => {
    return HttpResponse.json({ id: 'umbral-1', nota_maxima: 100, nota_minima: 0, umbral_atraso: 15, umbral_promocion: 80 })
  }),

  http.put('/api/calificaciones/:comisionId/umbral', () => {
    return HttpResponse.json({ id: 'umbral-1', nota_maxima: 100, nota_minima: 10, umbral_atraso: 15, umbral_promocion: 80 })
  }),

  // Entregas
  http.get('/api/entregas/pendientes', () => {
    const items = [
      { entrega_id: 'e-1', alumno_id: 'a-1', alumno_nombre: 'Juan Perez', actividad: 'TP 1', materia: 'Matemática', comision: 'A', fecha_entrega: '2026-05-10', dias_pendiente: 5 },
      { entrega_id: 'e-2', alumno_id: 'a-2', alumno_nombre: 'Maria Gomez', actividad: 'TP 2', materia: 'Lengua', comision: 'B', fecha_entrega: '2026-05-08', dias_pendiente: 7 },
    ]
    return HttpResponse.json({ items, total: items.length })
  }),

  http.get('/api/entregas/pendientes/exportar', () => {
    return HttpResponse.arrayBuffer(new ArrayBuffer(0), {
      headers: { 'Content-Type': 'text/csv' },
    })
  }),

  http.post('/api/calificaciones/completion-report', () => {
    return HttpResponse.json({
      materia_id: '00000000-0000-0000-0000-000000000001',
      cohorte_id: '00000000-0000-0000-0000-000000000002',
      posibles_entregas_sin_corregir: [
        { alumno_nombre: 'Juan', alumno_apellidos: 'Perez', actividad: 'Trabajo Final' },
      ],
    })
  }),

  // Comunicaciones
  http.post('/api/comunicaciones/preview', () => {
    return HttpResponse.json({
      asunto_renderizado: 'Aviso importante',
      cuerpo_renderizado: 'Estimado alumno, le informamos...',
    })
  }),

  http.post('/api/comunicaciones/enviar', () => {
    return HttpResponse.json(
      { lote_id: '00000000-0000-0000-0000-0000000000aa', mensajes_creados: 2 },
      { status: 201 },
    )
  }),

  http.get('/api/comunicaciones/lotes', () => {
    return HttpResponse.json({
      items: [
        {
          lote_id: '00000000-0000-0000-0000-0000000000aa',
          materia_id: '00000000-0000-0000-0000-000000000001',
          total: 2,
          pendientes: 2,
          enviados: 0,
          errores: 0,
          cancelados: 0,
          created_at: '2026-05-15T10:00:00Z',
        },
      ],
      total: 1,
    })
  }),

  http.get('/api/comunicaciones/lotes/:loteId', ({ params }) => {
    return HttpResponse.json({
      lote_id: params.loteId,
      materia_id: '00000000-0000-0000-0000-000000000001',
      comunicaciones: [
        {
          id: '00000000-0000-0000-0000-0000000000b1',
          materia_id: '00000000-0000-0000-0000-000000000001',
          destinatario: 'juan@test.com',
          asunto: 'Aviso importante',
          cuerpo: 'Estimado alumno...',
          estado: 'Pendiente',
          lote_id: params.loteId,
          enviado_at: null,
          created_at: '2026-05-15T10:00:00Z',
          updated_at: '2026-05-15T10:00:00Z',
        },
      ],
    })
  }),

  http.post('/api/comunicaciones/lotes/:loteId/aprobar', () => {
    return HttpResponse.json({ mensaje: 'Lote aprobado', afectados: 2 })
  }),

  http.post('/api/comunicaciones/lotes/:loteId/cancelar', () => {
    return HttpResponse.json({ mensaje: 'Lote cancelado', afectados: 2 })
  }),

  http.post('/api/comunicaciones/:comunicacionId/cancelar', () => {
    return HttpResponse.json({ mensaje: 'Comunicación cancelada', afectados: 1 })
  }),

  // Monitor
  http.get('/api/monitor/alumnos', () => {
    return HttpResponse.json([
      { alumno_id: 'a-1', alumno_nombre: 'Juan Perez', comision: 'COM-001', materia: 'Matemática', actividades_pendientes: 2, entregas_sin_corregir: 1, promedio_actual: 85, asistencias: 90, estado: 'al_dia', ultima_actividad: '2026-05-10' },
      { alumno_id: 'a-2', alumno_nombre: 'Maria Gomez', comision: 'COM-001', materia: 'Matemática', actividades_pendientes: 5, entregas_sin_corregir: 3, promedio_actual: 60, asistencias: 70, estado: 'atrasado', ultima_actividad: '2026-04-20' },
    ])
  }),
]
