"""Servicios de calificaciones: importación, matching, derivación de aprobado."""

import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calificaciones import Calificacion, OrigenCalificacion
from app.models.padron import EntradaPadron, VersionPadron
from app.repositories.calificaciones import (
    DEFAULT_UMBRAL_PCT,
    DEFAULT_VALORES_APROBATORIOS,
    CalificacionRepository,
    UmbralMateriaRepository,
)
from app.repositories.padron import EntradaPadronRepository, VersionPadronRepository
from app.services.lms_parser import LmsParseError, LMSFileParser, ParsedRow


class CalificacionError(ValueError):
    """Error de dominio en operaciones de calificaciones."""


class PreviewExpiredError(CalificacionError):
    """El preview ha expirado (TTL 10 min)."""


# ── Preview Cache ───────────────────────────────────────────────

PREVIEW_TTL_SECONDS = 10 * 60  # 10 minutos

_calif_preview_cache: dict[str, Any] = {}


@dataclass
class PreviewEntry:
    """Entrada de preview de calificaciones almacenada en caché."""

    materia_id: UUID
    cohorte_id: UUID
    entradas_padron: list[EntradaPadron]
    entradas_map: dict[UUID, EntradaPadron]  # entrada_padron_id -> entrada
    actividades: list[dict[str, str]]  # [{nombre, tipo}]
    matched_rows: list[dict[str, Any]]  # [{entrada_padron_id, nombre, apellidos, email, datos_actividad}]
    unmatched_rows: list[dict[str, Any]]  # [{fila, datos}]
    total_rows: int
    created_at: float = field(default_factory=time.time)


def _limpiar_calif_previews() -> None:
    """Elimina entradas expiradas del caché de previews."""
    now = time.time()
    expirados = [k for k, v in _calif_preview_cache.items() if now - v.created_at > PREVIEW_TTL_SECONDS]
    for k in expirados:
        del _calif_preview_cache[k]


def guardar_calif_preview(entry: PreviewEntry) -> str:
    """Guarda un preview de calificaciones y devuelve el token."""
    _limpiar_calif_previews()
    token = str(uuid.uuid4())
    _calif_preview_cache[token] = entry
    return token


def obtener_calif_preview(token: str) -> PreviewEntry | None:
    """Recupera un preview de calificaciones por token."""
    _limpiar_calif_previews()
    entry = _calif_preview_cache.get(token)
    if entry is None:
        return None
    if time.time() - entry.created_at > PREVIEW_TTL_SECONDS:
        del _calif_preview_cache[token]
        return None
    return entry


def eliminar_calif_preview(token: str) -> None:
    """Elimina un preview del caché."""
    _calif_preview_cache.pop(token, None)


# ── Derivación de aprobado ──────────────────────────────────────


def derivar_aprobado(
    nota_numerica: float | None,
    nota_textual: str | None,
    umbral_pct: int = DEFAULT_UMBRAL_PCT,
    valores_aprobatorios: list[str] | None = None,
) -> bool:
    """Deriva si una calificación está aprobada.

    Args:
        nota_numerica: Nota numérica (0-100 escala o similar).
        nota_textual: Nota textual (ej. "Satisfactorio").
        umbral_pct: Porcentaje mínimo para aprobar (default 60).
        valores_aprobatorios: Lista de valores textuales que se consideran aprobados.

    Returns:
        True si está aprobada, False en caso contrario.
    """
    if nota_numerica is not None:
        return nota_numerica >= umbral_pct
    if nota_textual is not None:
        valores = valores_aprobatorios or DEFAULT_VALORES_APROBATORIOS
        return nota_textual.strip() in valores
    return False


# ── Servicios ───────────────────────────────────────────────────


class CalificacionService:
    """Orquesta operaciones de calificaciones vía repositorios."""

    def __init__(self, session: AsyncSession, tenant_id: UUID, usuario_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.usuario_id = usuario_id
        self.calif_repo = CalificacionRepository(session, tenant_id)
        self.umbral_repo = UmbralMateriaRepository(session, tenant_id)
        self.version_repo = VersionPadronRepository(session, tenant_id)
        self.entrada_repo = EntradaPadronRepository(session, tenant_id)

    async def importar_grades(
        self, materia_id: UUID, cohorte_id: UUID, filename: str, contenido: bytes
    ) -> dict[str, Any]:
        """Paso 1: Parsea archivo LMS, matchea contra padrón activo, genera preview.

        Args:
            materia_id: UUID de la materia.
            cohorte_id: UUID de la cohorte.
            filename: Nombre del archivo.
            contenido: Contenido binario del archivo.

        Returns:
            Dict con preview_token, actividades, alumnos_match, alumnos_no_match, total_rows.

        Raises:
            LmsParseError: Si el archivo no se puede parsear.
            CalificacionError: Si no hay padrón activo.
        """
        # Obtener versión activa del padrón
        version_activa = await self.version_repo.get_activa(materia_id, cohorte_id)
        if version_activa is None:
            raise CalificacionError(
                "No hay una versión activa del padrón para esta materia×cohorte. "
                "Importe el padrón primero."
            )

        # Obtener entradas del padrón activo
        entradas = await self.listar_entradas_por_version(version_activa.id)

        # Parsear archivo
        resultado = LMSFileParser.parse(filename, contenido)

        if not resultado.columnas_actividad:
            raise CalificacionError(
                "No se detectaron columnas de actividad en el archivo. "
                "Asegúrese de que el archivo contiene calificaciones."
            )

        # Matchear alumnos
        matched_rows: list[dict[str, Any]] = []
        unmatched_rows: list[dict[str, Any]] = []
        entrada_map: dict[UUID, EntradaPadron] = {}
        for e in entradas:
            entrada_map[e.id] = e

        # Build lookup dicts for matching
        email_map: dict[str, EntradaPadron] = {}
        nombre_apellido_map: dict[tuple[str, str], EntradaPadron] = {}
        for e in entradas:
            email_lower = e.email.strip().lower() if e.email else ""
            if email_lower:
                email_map[email_lower] = e
            key = (e.nombre.strip().lower(), e.apellidos.strip().lower())
            nombre_apellido_map[key] = e

        for fila in resultado.filas:
            matched_entry = _match_entrada(fila, email_map, nombre_apellido_map)
            if matched_entry is not None:
                datos_act: dict[str, str | float | None] = {}
                for act_col in resultado.columnas_actividad:
                    raw_val = fila.datos_actividades.get(act_col.nombre)
                    if act_col.tipo == "numeric" and raw_val is not None:
                        try:
                            datos_act[act_col.nombre] = float(raw_val)
                        except (ValueError, TypeError):
                            datos_act[act_col.nombre] = raw_val
                    else:
                        datos_act[act_col.nombre] = raw_val
                matched_rows.append({
                    "entrada_padron_id": matched_entry.id,
                    "nombre": matched_entry.nombre,
                    "apellidos": matched_entry.apellidos,
                    "email": matched_entry.email,
                    "datos_actividad": datos_act,
                })
            else:
                unmatched_rows.append({
                    "fila": fila.fila,
                    "datos": dict(fila.datos_identidad),
                })

        # Build actividades preview
        actividades = [
            {"nombre": a.nombre, "tipo": a.tipo}
            for a in resultado.columnas_actividad
        ]

        # Guardar preview
        preview_entry = PreviewEntry(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            entradas_padron=entradas,
            entradas_map=entrada_map,
            actividades=actividades,
            matched_rows=matched_rows,
            unmatched_rows=unmatched_rows,
            total_rows=resultado.total_filas,
        )
        preview_token = guardar_calif_preview(preview_entry)

        # Build response
        alumnos_match = [
            {
                "entrada_padron_id": str(r["entrada_padron_id"]),
                "nombre": r["nombre"],
                "apellidos": r["apellidos"],
                "email": r["email"],
                "datos": r["datos_actividad"],
            }
            for r in matched_rows
        ]

        return {
            "preview_token": preview_token,
            "materia_id": materia_id,
            "cohorte_id": cohorte_id,
            "actividades": actividades,
            "total_rows": resultado.total_filas,
            "alumnos_match": alumnos_match,
            "alumnos_no_match": unmatched_rows,
            "total_match": len(matched_rows),
            "total_no_match": len(unmatched_rows),
        }

    async def confirmar_import(
        self, preview_token: str, actividad_ids: list[str]
    ) -> dict[str, Any]:
        """Paso 2: Confirma la importación usando un token de preview.

        Args:
            preview_token: Token del preview.
            actividad_ids: Lista de nombres de actividad a importar.

        Returns:
            Dict con materia_id, cohorte_id, registros_creados, actividades_importadas.

        Raises:
            PreviewExpiredError: Si el token expiró o es inválido.
        """
        preview = obtener_calif_preview(preview_token)
        if preview is None:
            raise PreviewExpiredError("El preview ha expirado o es inválido (TTL: 10 min)")

        # Obtener umbral
        umbral_info = UmbralMateriaRepository.get_default()

        # Obtener el umbral configurado si existe
        # Usamos el first matched row para buscar el umbral  TODO: mejorar scope
        if preview.matched_rows:
            entrada_id = preview.matched_rows[0]["entrada_padron_id"]
            entrada = preview.entradas_map.get(entrada_id)
            if entrada and hasattr(entrada, 'version_id'):
                # Buscar versión para obtener materia_id, etc
                pass

        # Filtrar actividades seleccionadas
        actividades_a_importar = [
            a for a in preview.actividades
            if a["nombre"] in actividad_ids
        ]

        if not actividades_a_importar:
            raise CalificacionError("No se seleccionaron actividades para importar")

        # Crear registros
        calificaciones: list[Calificacion] = []
        now = datetime.now(UTC)

        for row in preview.matched_rows:
            entrada_padron_id: UUID = row["entrada_padron_id"]
            datos = row["datos_actividad"]
            for act in actividades_a_importar:
                nombre_act = act["nombre"]
                raw_val = datos.get(nombre_act)
                nota_num: float | None = None
                nota_text: str | None = None

                if raw_val is not None:
                    if act["tipo"] == "numeric":
                        try:
                            nota_num = float(raw_val)
                        except (ValueError, TypeError):
                            nota_text = str(raw_val)
                    else:
                        nota_text = str(raw_val)

                aprobado = derivar_aprobado(nota_num, nota_text, umbral_info["umbral_pct"])

                cal = Calificacion(
                    tenant_id=self.tenant_id,
                    entrada_padron_id=entrada_padron_id,
                    materia_id=preview.materia_id,
                    actividad=nombre_act,
                    nota_numerica=nota_num,
                    nota_textual=nota_text,
                    aprobado=aprobado,
                    origen=OrigenCalificacion.IMPORTADO,
                    importado_at=now,
                )
                calificaciones.append(cal)

        created = await self.calif_repo.create_batch(calificaciones)
        count = len(created)
        eliminar_calif_preview(preview_token)

        # Registrar auditoría
        await self._registrar_auditoria_importacion(
            materia_id=preview.materia_id,
            actividades=actividad_ids,
            count=count,
        )

        return {
            "materia_id": preview.materia_id,
            "cohorte_id": preview.cohorte_id,
            "registros_creados": count,
            "actividades_importadas": actividad_ids,
        }

    async def importar_completion_report(
        self, materia_id: UUID, cohorte_id: UUID, filename: str, contenido: bytes
    ) -> dict[str, Any]:
        """Parsea un reporte de finalización y detecta entregas sin corregir.

        Solo aplica a actividades textuales (RN-08). Las actividades numéricas
        sin calificar NO se reportan.

        Args:
            materia_id: UUID de la materia.
            cohorte_id: UUID de la cohorte.
            filename: Nombre del archivo.
            contenido: Contenido binario del archivo.

        Returns:
            Dict con materia_id, cohorte_id, posibles_entregas_sin_corregir.
        """
        version_activa = await self.version_repo.get_activa(materia_id, cohorte_id)
        if version_activa is None:
            raise CalificacionError("No hay padrón activo para esta materia×cohorte")

        entradas = await self.listar_entradas_por_version(version_activa.id)
        entrada_map: dict[UUID, EntradaPadron] = {e.id: e for e in entradas}

        # Parsear archivo de finalización
        resultado = LMSFileParser.parse(filename, contenido)

        # Filtrar solo actividades textuales (RN-08)
        textual_activities = [
            a for a in resultado.columnas_actividad if a.tipo == "textual"
        ]

        # Build email/nombre lookup
        email_map: dict[str, EntradaPadron] = {}
        nombre_apellido_map: dict[tuple[str, str], EntradaPadron] = {}
        for e in entradas:
            email_lower = e.email.strip().lower() if e.email else ""
            if email_lower:
                email_map[email_lower] = e
            key = (e.nombre.strip().lower(), e.apellidos.strip().lower())
            nombre_apellido_map[key] = e

        # Detectar entregas sin calificar
        sin_corregir: list[dict[str, Any]] = []

        for fila in resultado.filas:
            matched = _match_entrada(fila, email_map, nombre_apellido_map)
            if matched is None:
                continue

            for act in textual_activities:
                raw_val = fila.datos_actividades.get(act.nombre)
                # Si tiene valor y está "entregado" pero no tiene calificación textual
                if raw_val is not None and raw_val.strip():
                    # Verificar si existe calificación para esta entrada+actividad
                    exists = await self.calif_repo.exists_for_entrada_actividad(
                        matched.id, act.nombre
                    )
                    if not exists:
                        sin_corregir.append({
                            "alumno_nombre": matched.nombre,
                            "alumno_apellidos": matched.apellidos,
                            "actividad": act.nombre,
                        })

        return {
            "materia_id": materia_id,
            "cohorte_id": cohorte_id,
            "posibles_entregas_sin_corregir": sin_corregir,
        }

    async def listar_calificaciones(self, materia_id: UUID) -> dict[str, Any]:
        """Lista calificaciones de una materia."""
        calificaciones = await self.calif_repo.list_by_materia(materia_id)
        return {
            "items": [
                {
                    "id": c.id,
                    "tenant_id": c.tenant_id,
                    "entrada_padron_id": c.entrada_padron_id,
                    "materia_id": c.materia_id,
                    "actividad": c.actividad,
                    "nota_numerica": c.nota_numerica,
                    "nota_textual": c.nota_textual,
                    "aprobado": c.aprobado,
                    "origen": c.origen.value if hasattr(c.origen, 'value') else c.origen,
                    "importado_at": c.importado_at,
                    "created_at": c.created_at,
                    "updated_at": c.updated_at,
                    "deleted_at": c.deleted_at,
                }
                for c in calificaciones
            ],
            "total": len(calificaciones),
        }

    async def _registrar_auditoria_importacion(
        self,
        materia_id: UUID,
        actividades: list[str],
        count: int,
    ) -> None:
        """Registra la importación en el log de auditoría.

        Si el modelo AuditLog no existe (C-05 no implementada), omite
        silenciosamente el registro de auditoría.
        """
        try:
            from app.models.audit import AuditLog  # noqa: PLC0415
            from sqlalchemy import insert  # noqa: PLC0415

            audit_entry = AuditLog(
                tenant_id=self.tenant_id,
                actor_id=self.usuario_id,
                accion="CALIFICACIONES_IMPORTAR",
                recurso_id=str(materia_id),
                recurso_tipo="materia",
                detalle={
                    "actividades": actividades,
                    "registros_creados": count,
                    "materia_id": str(materia_id),
                },
            )
            self.session.add(audit_entry)
        except (ImportError, Exception):
            # C-05 audit log no disponible o error al grabar
            pass

    async def listar_entradas_por_version(
        self, version_id: UUID
    ) -> list[EntradaPadron]:
        """Lista entradas activas para una versión de padrón."""
        result = await self.session.execute(
            select(EntradaPadron).where(
                EntradaPadron.tenant_id == self.tenant_id,
                EntradaPadron.version_id == version_id,
                EntradaPadron.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())


def _match_entrada(
    fila: ParsedRow,
    email_map: dict[str, "EntradaPadron"],
    nombre_apellido_map: dict[tuple[str, str], "EntradaPadron"],
) -> "EntradaPadron | None":
    """Matchea una fila del archivo contra el padrón activo.

    Estrategia: primero por email, luego por nombre+apellido compuesto.

    Args:
        fila: Fila parseada del archivo LMS.
        email_map: Dict email -> EntradaPadron.
        nombre_apellido_map: Dict (nombre, apellidos) -> EntradaPadron.

    Returns:
        EntradaPadron si hay match, None en caso contrario.
    """
    email_value = fila.datos_identidad.get("email", "").strip().lower()
    if email_value and email_value in email_map:
        return email_map[email_value]

    nombre_value = fila.datos_identidad.get("nombre", "").strip().lower()
    apellidos_value = fila.datos_identidad.get("apellidos", "").strip().lower()

    # Try full name match
    if nombre_value and apellidos_value:
        key = (nombre_value, apellidos_value)
        if key in nombre_apellido_map:
            return nombre_apellido_map[key]

    return None


class UmbralMateriaService:
    """Servicio de configuración de umbral de aprobación."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.umbral_repo = UmbralMateriaRepository(session, tenant_id)

    async def obtener(
        self, asignacion_id: UUID, materia_id: UUID
    ) -> dict[str, Any]:
        """Devuelve el umbral configurado o el default.

        Args:
            asignacion_id: UUID de la asignación docente.
            materia_id: UUID de la materia.

        Returns:
            Dict con id (opcional), asignacion_id, materia_id, umbral_pct, valores_aprobatorios.
        """
        umbral = await self.umbral_repo.get_by_asignacion(asignacion_id, materia_id)
        if umbral is not None:
            return {
                "id": str(umbral.id),
                "tenant_id": umbral.tenant_id,
                "asignacion_id": str(umbral.asignacion_id),
                "materia_id": str(umbral.materia_id),
                "umbral_pct": umbral.umbral_pct,
                "valores_aprobatorios": umbral.valores_aprobatorios or [],
                "created_at": umbral.created_at,
                "updated_at": umbral.updated_at,
                "deleted_at": umbral.deleted_at,
            }
        default = UmbralMateriaRepository.get_default()
        return {
            "id": None,
            "tenant_id": self.tenant_id,
            "asignacion_id": str(asignacion_id),
            "materia_id": str(materia_id),
            "umbral_pct": default["umbral_pct"],
            "valores_aprobatorios": default["valores_aprobatorios"],
            "created_at": None,
            "updated_at": None,
            "deleted_at": None,
        }

    async def configurar(
        self,
        asignacion_id: UUID,
        materia_id: UUID,
        umbral_pct: int,
        valores_aprobatorios: list[str] | None = None,
    ) -> dict[str, Any]:
        """Crea o actualiza el UmbralMateria.

        Args:
            asignacion_id: UUID de la asignación docente.
            materia_id: UUID de la materia.
            umbral_pct: Porcentaje mínimo para aprobar.
            valores_aprobatorios: Lista de valores textuales aprobatorios.

        Returns:
            Dict con el umbral actualizado.
        """
        if umbral_pct < 0 or umbral_pct > 100:
            raise CalificacionError("umbral_pct must be between 0 and 100")

        umbral = await self.umbral_repo.upsert(
            asignacion_id=asignacion_id,
            materia_id=materia_id,
            data={
                "umbral_pct": umbral_pct,
                "valores_aprobatorios": valores_aprobatorios,
            },
        )
        return {
            "id": str(umbral.id),
            "tenant_id": umbral.tenant_id,
            "asignacion_id": str(umbral.asignacion_id),
            "materia_id": str(umbral.materia_id),
            "umbral_pct": umbral.umbral_pct,
            "valores_aprobatorios": umbral.valores_aprobatorios or [],
            "created_at": umbral.created_at,
            "updated_at": umbral.updated_at,
            "deleted_at": umbral.deleted_at,
        }
