"""Repositorio tenant-scoped para análisis de calificaciones y reportes.

Todas las consultas operan sobre datos existentes (C-06, C-07, C-09, C-10).
NO crea nuevas tablas ni migraciones.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Float, func, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calificaciones import Calificacion, UmbralMateria
from app.models.padron import EntradaPadron, VersionPadron

DEFAULT_UMBRAL = 60


class AnalisisRepository:
    """Consultas de análisis sobre calificaciones y padrón.

    NO extiende TenantScopedRepository porque opera sobre MÚLTIPLES modelos.
    Mantiene tenant_id obligatorio para fail-closed.
    """

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id

    # ── 2.1 — listar_atrasados ─────────────────────────────────

    async def listar_atrasados(self, materia_id: UUID) -> list[dict]:
        """Lista alumnos atrasados para una materia (RN-06).

        Detecta:
        - Actividades SIN calificación (faltantes).
        - Actividades CON calificación pero nota < umbral (nota_insuficiente).

        Returns:
            Lista de dicts con entrada_padron_id, alumno_nombre,
            actividades_atrasadas (list[dict] con actividad y motivo).
        """
        # 1. Obtener versión activa del padrón
        result = await self.session.execute(
            select(VersionPadron).where(
                VersionPadron.tenant_id == self.tenant_id,
                VersionPadron.materia_id == materia_id,
                VersionPadron.activa.is_(True),
                VersionPadron.deleted_at.is_(None),
            )
        )
        version = result.scalar_one_or_none()
        if version is None:
            return []

        # 2. Obtener entradas del padrón activo
        result = await self.session.execute(
            select(EntradaPadron).where(
                EntradaPadron.tenant_id == self.tenant_id,
                EntradaPadron.version_id == version.id,
                EntradaPadron.deleted_at.is_(None),
            )
        )
        entradas = list(result.scalars().all())
        if not entradas:
            return []

        # 3. Obtener todas las calificaciones de la materia
        result = await self.session.execute(
            select(Calificacion).where(
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.materia_id == materia_id,
                Calificacion.deleted_at.is_(None),
            )
        )
        calificaciones = list(result.scalars().all())
        if not calificaciones:
            return []

        # 4. Derivar actividades conocidas (todas las que existen en calificaciones)
        actividades = sorted({c.actividad for c in calificaciones})

        # 5. Construir lookup: (entrada_padron_id, actividad) -> Calificacion
        calif_map: dict[tuple[UUID, str], Calificacion] = {}
        for c in calificaciones:
            calif_map[(c.entrada_padron_id, c.actividad)] = c

        # 6. Obtener umbral (default 60)
        umbral_pct = DEFAULT_UMBRAL

        # 7. Por cada alumno, detectar atrasos
        resultado: list[dict] = []
        for entrada in entradas:
            atrasadas: list[dict] = []
            for act in actividades:
                calif = calif_map.get((entrada.id, act))
                if calif is None:
                    atrasadas.append({"actividad": act, "motivo": "falta"})
                elif not calif.aprobado:
                    atrasadas.append({"actividad": act, "motivo": "nota_insuficiente"})
            if atrasadas:
                resultado.append({
                    "entrada_padron_id": entrada.id,
                    "alumno_nombre": f"{entrada.nombre} {entrada.apellidos}".strip(),
                    "actividades_atrasadas": atrasadas,
                })

        return resultado

    # ── 2.2 — ranking_aprobados ─────────────────────────────────

    async def ranking_aprobados(self, materia_id: UUID) -> list[dict]:
        """Ranking de alumnos por actividades aprobadas (RN-09).

        Excluye alumnos sin ninguna actividad aprobada.
        Ordena descendente por count, luego alfabético por nombre.

        Returns:
            Lista de dicts con ranking, entrada_padron_id, alumno_nombre,
            actividades_aprobadas.
        """
        # Subquery: count approved per student
        stmt = (
            select(
                Calificacion.entrada_padron_id,
                func.count(
                    case((Calificacion.aprobado.is_(True), 1), else_=None)
                ).label("actividades_aprobadas"),
            )
            .where(
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.materia_id == materia_id,
                Calificacion.deleted_at.is_(None),
            )
            .group_by(Calificacion.entrada_padron_id)
            .having(
                func.count(
                    case((Calificacion.aprobado.is_(True), 1), else_=None)
                ) >= 1
            )
            .order_by(
                func.count(
                    case((Calificacion.aprobado.is_(True), 1), else_=None)
                ).desc(),
                # We'll sort alphabetically in Python after joining names
            )
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        if not rows:
            return []

        # Get student names
        entrada_ids = [r.entrada_padron_id for r in rows]
        entry_result = await self.session.execute(
            select(EntradaPadron).where(
                EntradaPadron.tenant_id == self.tenant_id,
                EntradaPadron.id.in_(entrada_ids),
                EntradaPadron.deleted_at.is_(None),
            )
        )
        entradas = {e.id: e for e in list(entry_result.scalars().all())}

        # Build ranking with names
        ranking = []
        for r in rows:
            entry = entradas.get(r.entrada_padron_id)
            nombre = f"{entry.nombre} {entry.apellidos}".strip() if entry else "Desconocido"
            ranking.append({
                "entrada_padron_id": r.entrada_padron_id,
                "alumno_nombre": nombre,
                "actividades_aprobadas": r.actividades_aprobadas,
            })

        # Sort: desc by count, then asc by nombre
        ranking.sort(key=lambda x: (-x["actividades_aprobadas"], x["alumno_nombre"]))

        # Assign ranking positions
        for i, item in enumerate(ranking):
            item["ranking"] = i + 1

        return ranking

    # ── 2.3 — reportes_rapidos ──────────────────────────────────

    async def reportes_rapidos(self, materia_id: UUID) -> dict:
        """Métricas consolidadas por materia.

        Returns:
            Dict con total_alumnos, total_calificaciones, promedio_general,
            total_aprobados, total_no_aprobados, desglose_por_actividad.
        """
        # 1. Total alumnos en padrón activo
        result = await self.session.execute(
            select(VersionPadron).where(
                VersionPadron.tenant_id == self.tenant_id,
                VersionPadron.materia_id == materia_id,
                VersionPadron.activa.is_(True),
                VersionPadron.deleted_at.is_(None),
            )
        )
        version = result.scalar_one_or_none()
        total_alumnos = 0
        if version is not None:
            count_result = await self.session.execute(
                select(func.count()).where(
                    EntradaPadron.tenant_id == self.tenant_id,
                    EntradaPadron.version_id == version.id,
                    EntradaPadron.deleted_at.is_(None),
                )
            )
            total_alumnos = count_result.scalar() or 0

        # 2. Métricas de calificaciones
        result = await self.session.execute(
            select(
                func.count().label("total"),
                func.avg(Calificacion.nota_numerica).label("promedio"),
                func.sum(case((Calificacion.aprobado.is_(True), 1), else_=0)).label("aprobados"),
            ).where(
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.materia_id == materia_id,
                Calificacion.deleted_at.is_(None),
            )
        )
        row = result.one()
        total_calificaciones = row.total or 0
        promedio_general = round(float(row.promedio), 2) if row.promedio is not None else 0.0
        total_aprobados = row.aprobados or 0
        total_no_aprobados = total_calificaciones - total_aprobados

        # 3. Desglose por actividad
        result = await self.session.execute(
            select(
                Calificacion.actividad,
                func.count().label("presentado"),
                func.avg(Calificacion.nota_numerica).label("promedio"),
                func.min(Calificacion.nota_numerica).label("min"),
                func.max(Calificacion.nota_numerica).label("max"),
            ).where(
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.materia_id == materia_id,
                Calificacion.deleted_at.is_(None),
            ).group_by(Calificacion.actividad)
        )
        desglose = []
        for r in result.all():
            desglose.append({
                "actividad": r.actividad,
                "presentado": r.presentado,
                "promedio": round(float(r.promedio), 2) if r.promedio is not None else None,
                "min": round(float(r.min), 2) if r.min is not None else None,
                "max": round(float(r.max), 2) if r.max is not None else None,
            })

        return {
            "total_alumnos": total_alumnos,
            "total_calificaciones": total_calificaciones,
            "promedio_general": promedio_general,
            "total_aprobados": total_aprobados,
            "total_no_aprobados": total_no_aprobados,
            "desglose_por_actividad": desglose,
        }

    # ── 2.4 — notas_finales ─────────────────────────────────────

    async def notas_finales(
        self, materia_id: UUID, actividades: list[str]
    ) -> list[dict]:
        """Calcula nota final por alumno promediando actividades seleccionadas.

        Args:
            materia_id: UUID de la materia.
            actividades: Lista de nombres de actividad a incluir.

        Returns:
            Lista de dicts con entrada_padron_id, alumno_nombre,
            promedio, aprobado.
        """
        if not actividades:
            return []

        result = await self.session.execute(
            select(Calificacion).where(
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.materia_id == materia_id,
                Calificacion.actividad.in_(actividades),
                Calificacion.nota_numerica.isnot(None),
                Calificacion.deleted_at.is_(None),
            )
        )
        calificaciones = list(result.scalars().all())

        if not calificaciones:
            return []

        # Get student names
        entrada_ids = list({c.entrada_padron_id for c in calificaciones})
        entry_result = await self.session.execute(
            select(EntradaPadron).where(
                EntradaPadron.tenant_id == self.tenant_id,
                EntradaPadron.id.in_(entrada_ids),
                EntradaPadron.deleted_at.is_(None),
            )
        )
        entradas = {e.id: e for e in list(entry_result.scalars().all())}

        # Group by student and calculate average of numeric grades
        from collections import defaultdict
        student_grades: dict[UUID, list[float]] = defaultdict(list)
        for c in calificaciones:
            if c.nota_numerica is not None:
                student_grades[c.entrada_padron_id].append(c.nota_numerica)

        resultado = []
        for entrada_id, notas in student_grades.items():
            if not notas:
                continue
            promedio = sum(notas) / len(notas)
            entry = entradas.get(entrada_id)
            nombre = f"{entry.nombre} {entry.apellidos}".strip() if entry else "Desconocido"
            resultado.append({
                "entrada_padron_id": entrada_id,
                "alumno_nombre": nombre,
                "promedio": round(promedio, 2),
                "aprobado": promedio >= DEFAULT_UMBRAL,
            })

        return resultado

    # ── 2.5 — tps_sin_corregir ──────────────────────────────────

    async def tps_sin_corregir(self, materia_id: UUID) -> list[dict]:
        """Detecta TPs textuales sin calificar (RN-07/08).

        Reporta actividades textual-scale donde el alumno no tiene
        Calificacion. Ignora actividades numéricas sin calificación.

        Returns:
            Lista de dicts con alumno_nombre, actividad, materia_id.
        """
        # 1. Get active version + entries
        result = await self.session.execute(
            select(VersionPadron).where(
                VersionPadron.tenant_id == self.tenant_id,
                VersionPadron.materia_id == materia_id,
                VersionPadron.activa.is_(True),
                VersionPadron.deleted_at.is_(None),
            )
        )
        version = result.scalar_one_or_none()
        if version is None:
            return []

        result = await self.session.execute(
            select(EntradaPadron).where(
                EntradaPadron.tenant_id == self.tenant_id,
                EntradaPadron.version_id == version.id,
                EntradaPadron.deleted_at.is_(None),
            )
        )
        entradas = list(result.scalars().all())
        if not entradas:
            return []

        # 2. Get all calificaciones for the materia
        result = await self.session.execute(
            select(Calificacion).where(
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.materia_id == materia_id,
                Calificacion.deleted_at.is_(None),
            )
        )
        calificaciones = list(result.scalars().all())

        # 3. Determine textual activities: an activity is "textual" if
        #    any of its Calificacion records have nota_textual set.
        act_by_type: dict[str, str] = {}  # actividad -> "numeric" or "textual"
        actividad_set: set[str] = set()
        for c in calificaciones:
            actividad_set.add(c.actividad)
            if c.nota_textual is not None:
                act_by_type[c.actividad] = "textual"
            elif c.actividad not in act_by_type:
                act_by_type[c.actividad] = "numeric"

        # 4. Build lookup of existing calificaciones per student
        student_califs: dict[UUID, set[str]] = {}
        for c in calificaciones:
            if c.entrada_padron_id not in student_califs:
                student_califs[c.entrada_padron_id] = set()
            student_califs[c.entrada_padron_id].add(c.actividad)

        # 5. For each student, find missing textual activities
        resultado: list[dict] = []
        for entrada in entradas:
            existing = student_califs.get(entrada.id, set())
            for act in sorted(actividad_set):
                if act_by_type.get(act) == "textual" and act not in existing:
                    nombre = f"{entrada.nombre} {entrada.apellidos}".strip()
                    resultado.append({
                        "alumno_nombre": nombre,
                        "actividad": act,
                        "materia_id": materia_id,
                    })

        return resultado

    # ── 2.6 — monitor general ───────────────────────────────────

    async def monitor(
        self, filtros: dict, limit: int = 50, offset: int = 0
    ) -> dict:
        """Monitor general con filtros dinámicos.

        Requiere al menos materia_id o busqueda para evitar queries sin filtro.

        Args:
            filtros: Dict con materia_id, regional, comision, busqueda,
                     actividad, min_actividad_cumplida.
            limit: Máximo de resultados por página.
            offset: Desplazamiento para paginación.

        Returns:
            Dict con data (lista), total (int).
        """
        materia_id = filtros.get("materia_id")
        busqueda = filtros.get("busqueda")

        if not materia_id and not busqueda:
            raise ValueError("Se requiere al menos materia_id o busqueda")

        # Build base query
        # We need: student data + count of activities + count of approved + atrasado status
        # Start by getting the relevant EntradaPadron records

        # Get padron entries scoped by materia or by busqueda
        query_entradas = (
            select(EntradaPadron)
            .where(
                EntradaPadron.tenant_id == self.tenant_id,
                EntradaPadron.deleted_at.is_(None),
            )
        )

        if materia_id:
            # Join through VersionPadron to filter by materia
            query_entradas = query_entradas.join(
                VersionPadron,
                (VersionPadron.id == EntradaPadron.version_id)
                & (VersionPadron.tenant_id == self.tenant_id)
                & (VersionPadron.deleted_at.is_(None))
                & (VersionPadron.activa.is_(True))
            ).where(VersionPadron.materia_id == materia_id)

        if busqueda:
            query_entradas = query_entradas.where(
                EntradaPadron.nombre.ilike(f"%{busqueda}%")
                | EntradaPadron.apellidos.ilike(f"%{busqueda}%")
                | EntradaPadron.email.ilike(f"%{busqueda}%")
            )

        if "regional" in filtros and filtros["regional"]:
            query_entradas = query_entradas.where(
                EntradaPadron.regional == filtros["regional"]
            )
        if "comision" in filtros and filtros["comision"]:
            query_entradas = query_entradas.where(
                EntradaPadron.comision == filtros["comision"]
            )

        # Get total count
        count_query = select(func.count()).select_from(query_entradas.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        result = await self.session.execute(
            query_entradas.order_by(EntradaPadron.apellidos, EntradaPadron.nombre)
            .offset(offset)
            .limit(limit)
        )
        entradas = list(result.scalars().all())

        if not entradas:
            return {"data": [], "total": total}

        # Get calificaciones for these students
        entrada_ids = [e.id for e in entradas]
        calif_result = await self.session.execute(
            select(Calificacion).where(
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.entrada_padron_id.in_(entrada_ids),
                Calificacion.deleted_at.is_(None),
            )
        )
        calificaciones = list(calif_result.scalars().all())

        # Optional: filter by actividad
        actividad_filter = filtros.get("actividad")
        if actividad_filter:
            calificaciones = [c for c in calificaciones if c.actividad == actividad_filter]

        # Group calificaciones by student
        from collections import defaultdict
        student_data: dict[UUID, dict] = defaultdict(lambda: {
            "total": 0, "aprobadas": 0, "pendientes": 0,
        })
        for c in calificaciones:
            student_data[c.entrada_padron_id]["total"] += 1
            if c.aprobado:
                student_data[c.entrada_padron_id]["aprobadas"] += 1
            else:
                student_data[c.entrada_padron_id]["pendientes"] += 1

        min_act = filtros.get("min_actividad_cumplida")

        data = []
        for entrada in entradas:
            sd = student_data.get(entrada.id, {"total": 0, "aprobadas": 0, "pendientes": 0})

            # Filter by min_actividad_cumplida
            if min_act is not None and sd["aprobadas"] < min_act:
                continue

            data.append({
                "entrada_padron_id": entrada.id,
                "alumno_nombre": f"{entrada.nombre} {entrada.apellidos}".strip(),
                "email": entrada.email,
                "regional": entrada.regional,
                "comision": entrada.comision,
                "total_actividades": sd["total"],
                "aprobadas": sd["aprobadas"],
                "pendientes": sd["pendientes"],
                "atrasado": sd["pendientes"] > 0,
            })

        return {"data": data, "total": total}

    # ── 2.7 — monitor_por_asignaciones ──────────────────────────

    async def monitor_por_asignaciones(
        self, filtros: dict, asignacion_ids: list[UUID],
        limit: int = 50, offset: int = 0,
    ) -> dict:
        """Monitor scoped a asignaciones específicas (TUTOR/PROFESOR).

        Args:
            filtros: Dict con materia_id, regional, comision, busqueda, etc.
            asignacion_ids: Lista de UUIDs de asignaciones para scoping.
            limit: Máximo de resultados.
            offset: Desplazamiento.

        Returns:
            Dict con data y total.
        """
        from app.models.usuarios_asignaciones import Asignacion

        materia_id = filtros.get("materia_id")
        busqueda = filtros.get("busqueda")

        if not materia_id and not busqueda:
            raise ValueError("Se requiere al menos materia_id o busqueda")

        # Get materia_ids from asignaciones
        result = await self.session.execute(
            select(Asignacion.materia_id).where(
                Asignacion.tenant_id == self.tenant_id,
                Asignacion.id.in_(asignacion_ids),
                Asignacion.deleted_at.is_(None),
            )
        )
        materia_ids = list({r[0] for r in result.all()})

        if not materia_ids:
            return {"data": [], "total": 0}

        # Filter by materia_id from filtros if present
        if materia_id is not None and materia_id in materia_ids:
            materia_ids = [materia_id]

        # Build query for EntradaPadron scoped to the resolved materia IDs
        query_entradas = (
            select(EntradaPadron)
            .where(
                EntradaPadron.tenant_id == self.tenant_id,
                EntradaPadron.deleted_at.is_(None),
            )
            .join(
                VersionPadron,
                (VersionPadron.id == EntradaPadron.version_id)
                & (VersionPadron.tenant_id == self.tenant_id)
                & (VersionPadron.deleted_at.is_(None))
                & (VersionPadron.activa.is_(True))
            )
            .where(VersionPadron.materia_id.in_(materia_ids))
        )

        if busqueda:
            query_entradas = query_entradas.where(
                EntradaPadron.nombre.ilike(f"%{busqueda}%")
                | EntradaPadron.apellidos.ilike(f"%{busqueda}%")
                | EntradaPadron.email.ilike(f"%{busqueda}%")
            )

        if "regional" in filtros and filtros["regional"]:
            query_entradas = query_entradas.where(
                EntradaPadron.regional == filtros["regional"]
            )
        if "comision" in filtros and filtros["comision"]:
            query_entradas = query_entradas.where(
                EntradaPadron.comision == filtros["comision"]
            )

        count_result = await self.session.execute(
            select(func.count()).select_from(query_entradas.subquery())
        )
        total = count_result.scalar() or 0

        result = await self.session.execute(
            query_entradas.order_by(EntradaPadron.apellidos, EntradaPadron.nombre)
            .offset(offset).limit(limit)
        )
        entradas = list(result.scalars().all())

        if not entradas:
            return {"data": [], "total": total}

        entrada_ids = [e.id for e in entradas]
        calif_result = await self.session.execute(
            select(Calificacion).where(
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.entrada_padron_id.in_(entrada_ids),
                Calificacion.deleted_at.is_(None),
            )
        )
        calificaciones = list(calif_result.scalars().all())

        from collections import defaultdict
        student_data: dict[UUID, dict] = defaultdict(lambda: {"total": 0, "aprobadas": 0, "pendientes": 0})
        for c in calificaciones:
            student_data[c.entrada_padron_id]["total"] += 1
            if c.aprobado:
                student_data[c.entrada_padron_id]["aprobadas"] += 1
            else:
                student_data[c.entrada_padron_id]["pendientes"] += 1

        data = []
        for entrada in entradas:
            sd = student_data.get(entrada.id, {"total": 0, "aprobadas": 0, "pendientes": 0})
            data.append({
                "entrada_padron_id": entrada.id,
                "alumno_nombre": f"{entrada.nombre} {entrada.apellidos}".strip(),
                "email": entrada.email,
                "regional": entrada.regional,
                "comision": entrada.comision,
                "total_actividades": sd["total"],
                "aprobadas": sd["aprobadas"],
                "pendientes": sd["pendientes"],
                "atrasado": sd["pendientes"] > 0,
            })

        return {"data": data, "total": total}

    # ── 2.8 — monitor_con_fechas ────────────────────────────────

    async def monitor_con_fechas(
        self, filtros: dict, desde: datetime, hasta: datetime,
        limit: int = 50, offset: int = 0,
    ) -> dict:
        """Monitor con filtro de rango de fechas en importado_at.

        Args:
            filtros: Dict con materia_id, regional, comision, busqueda, etc.
            desde: Fecha inicio del rango.
            hasta: Fecha fin del rango.
            limit: Máximo de resultados.
            offset: Desplazamiento.

        Returns:
            Dict con data y total.
        """
        materia_id = filtros.get("materia_id")
        busqueda = filtros.get("busqueda")

        if not materia_id and not busqueda:
            raise ValueError("Se requiere al menos materia_id o busqueda")

        query_entradas = (
            select(EntradaPadron)
            .where(
                EntradaPadron.tenant_id == self.tenant_id,
                EntradaPadron.deleted_at.is_(None),
            )
        )

        if materia_id:
            query_entradas = query_entradas.join(
                VersionPadron,
                (VersionPadron.id == EntradaPadron.version_id)
                & (VersionPadron.tenant_id == self.tenant_id)
                & (VersionPadron.deleted_at.is_(None))
                & (VersionPadron.activa.is_(True))
            ).where(VersionPadron.materia_id == materia_id)

        if busqueda:
            query_entradas = query_entradas.where(
                EntradaPadron.nombre.ilike(f"%{busqueda}%")
                | EntradaPadron.apellidos.ilike(f"%{busqueda}%")
                | EntradaPadron.email.ilike(f"%{busqueda}%")
            )

        if "regional" in filtros and filtros["regional"]:
            query_entradas = query_entradas.where(
                EntradaPadron.regional == filtros["regional"]
            )
        if "comision" in filtros and filtros["comision"]:
            query_entradas = query_entradas.where(
                EntradaPadron.comision == filtros["comision"]
            )

        count_result = await self.session.execute(
            select(func.count()).select_from(query_entradas.subquery())
        )
        total_estudiantes = count_result.scalar() or 0

        result = await self.session.execute(
            query_entradas.order_by(EntradaPadron.apellidos, EntradaPadron.nombre)
            .offset(offset).limit(limit)
        )
        entradas = list(result.scalars().all())

        if not entradas:
            return {"data": [], "total": total_estudiantes}

        entrada_ids = [e.id for e in entradas]
        calif_result = await self.session.execute(
            select(Calificacion).where(
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.entrada_padron_id.in_(entrada_ids),
                Calificacion.importado_at >= desde,
                Calificacion.importado_at <= hasta,
                Calificacion.deleted_at.is_(None),
            )
        )
        calificaciones = list(calif_result.scalars().all())

        from collections import defaultdict
        student_data: dict[UUID, dict] = defaultdict(lambda: {"total": 0, "aprobadas": 0, "pendientes": 0})
        for c in calificaciones:
            student_data[c.entrada_padron_id]["total"] += 1
            if c.aprobado:
                student_data[c.entrada_padron_id]["aprobadas"] += 1
            else:
                student_data[c.entrada_padron_id]["pendientes"] += 1

        data = []
        for entrada in entradas:
            sd = student_data.get(entrada.id, {"total": 0, "aprobadas": 0, "pendientes": 0})
            data.append({
                "entrada_padron_id": entrada.id,
                "alumno_nombre": f"{entrada.nombre} {entrada.apellidos}".strip(),
                "email": entrada.email,
                "regional": entrada.regional,
                "comision": entrada.comision,
                "total_actividades": sd["total"],
                "aprobadas": sd["aprobadas"],
                "pendientes": sd["pendientes"],
                "atrasado": sd["pendientes"] > 0,
            })

        return {"data": data, "total": total_estudiantes}
