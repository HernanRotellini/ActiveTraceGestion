"""Constantes tipadas de permisos del sistema.

Cada constante corresponde a un código de permiso del módulo RBAC.
Usar estas constantes en lugar de strings literales en decoradores
require_permission() para evitar typos.
"""

ACADEMICO_VER_ESTADO_PROPIO = "academico:ver_estado_propio"
EVALUACIONES_RESERVAR = "evaluaciones:reservar"
AVISOS_CONFIRMAR = "avisos:confirmar"
CALIFICACIONES_IMPORTAR = "calificaciones:importar"
ATRASADOS_VER = "atrasados:ver"
ENTREGAS_DETECTAR_SIN_CORREGIR = "entregas:detectar_sin_corregir"
COMUNICACION_ENVIAR = "comunicacion:enviar"
COMUNICACION_APROBAR = "comunicacion:aprobar"
ENCUENTROS_GESTIONAR = "encuentros:gestionar"
GUARDIAS_REGISTRAR = "guardias:registrar"
TAREAS_GESTIONAR = "tareas:gestionar"
AVISOS_PUBLICAR = "avisos:publicar"
EQUIPOS_ASIGNAR = "equipos:asignar"
ESTRUCTURA_GESTIONAR = "estructura:gestionar"
USUARIOS_GESTIONAR = "usuarios:gestionar"
COLOQUIOS_GESTIONAR = "coloquios:gestionar"
COLOQUIOS_RESERVAR = "coloquios:reservar"
AUDITORIA_VER = "auditoria:ver"
LIQUIDACIONES_OPERAR_GRILLA = "liquidaciones:operar_grilla"
LIQUIDACIONES_CALCULAR_CERRAR = "liquidaciones:calcular_cerrar"
FACTURAS_GESTIONAR = "facturas:gestionar"
TENANT_CONFIGURAR = "tenant:configurar"
IMPERSONACION_USAR = "impersonacion:usar"

# ── Audit action codes ──────────────────────────────────────────
CALIFICACIONES_IMPORTAR_ACTION = "CALIFICACIONES_IMPORTAR"
PADRON_CARGAR = "PADRON_CARGAR"
COMUNICACION_ENVIAR_ACTION = "COMUNICACION_ENVIAR"
COMUNICACION_APROBAR_ACTION = "COMUNICACION_APROBAR"
COMUNICACION_CANCELAR = "COMUNICACION_CANCELAR"
ASIGNACION_MODIFICAR = "ASIGNACION_MODIFICAR"
LIQUIDACION_CERRAR = "LIQUIDACION_CERRAR"
IMPERSONACION_INICIAR = "IMPERSONACION_INICIAR"
IMPERSONACION_FINALIZAR = "IMPERSONACION_FINALIZAR"
ANALISIS_EXPORTAR = "ANALISIS_EXPORTAR"
ANALISIS_CONSULTAR = "ANALISIS_CONSULTAR"
