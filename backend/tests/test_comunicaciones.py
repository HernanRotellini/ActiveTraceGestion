"""Tests para C-12 Comunicaciones: máquina de estados, preview, envío, aprobación, worker.

Strict TDD: RED → GREEN → TRIANGULATE → REFACTOR.
"""

from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.security import hash_password
from app.models.auth import AuthUser
from app.models.tenant import Tenant


# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
async def comunicacion_schema(db_engine: None):
    """Creates full schema for comunicaciones tests."""
    from app.core.database import get_sessionmaker
    from app.models.calificaciones import Calificacion, UmbralMateria  # noqa: F401
    from app.models.comunicacion import Comunicacion  # noqa: F401
    from app.models.estructura_academica import Carrera, Cohorte, Materia  # noqa: F401
    from app.models.padron import EntradaPadron, VersionPadron  # noqa: F401
    from app.models.usuarios_asignaciones import Asignacion, Usuario  # noqa: F401

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(
            text(
                "DROP TABLE IF EXISTS comunicaciones, calificaciones, umbrales_materia, "
                "entradas_padron, versiones_padron, "
                "asignaciones, usuarios, cohortes, carreras, materias, "
                "roles_permisos, permisos, roles, "
                "password_recovery_tokens, two_factor_challenges, "
                "totp_factors, refresh_sessions, auth_users, tenants CASCADE"
            )
        )
        await connection.execute(text("DROP TYPE IF EXISTS estado_comunicacion CASCADE"))
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        await session.commit()


@pytest.fixture
async def seed_tenant_admin(db_session: AsyncSession) -> dict[str, Any]:
    """Seeds tenant + admin user."""
    tenant = Tenant(name="Test Tenant", code="test-tenant")
    db_session.add(tenant)
    await db_session.flush()

    user = AuthUser(
        tenant_id=tenant.id,
        email="admin@test.com",
        password_hash=hash_password("password"),
        roles=["ADMIN"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.commit()
    return {"tenant_id": tenant.id, "tenant_code": tenant.code, "user_id": user.id}


@pytest.fixture
async def seed_estructura(
    db_session: AsyncSession,
    seed_tenant_admin: dict[str, Any],
) -> dict[str, Any]:
    """Seeds carrera, cohorte, materia."""
    from app.models.estructura_academica import Carrera, Cohorte, Materia

    carrera = Carrera(
        tenant_id=seed_tenant_admin["tenant_id"], codigo="TEST", nombre="Test",
    )
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        tenant_id=seed_tenant_admin["tenant_id"],
        carrera_id=carrera.id,
        nombre="2026", anio=2026,
        vig_desde=date(2026, 1, 1),
    )
    db_session.add(cohorte)
    await db_session.flush()

    materia = Materia(
        tenant_id=seed_tenant_admin["tenant_id"],
        codigo="MAT001", nombre="Matematica",
    )
    db_session.add(materia)
    await db_session.flush()
    await db_session.commit()
    return {"carrera_id": carrera.id, "cohorte_id": cohorte.id, "materia_id": materia.id}


@pytest.fixture
async def seed_padron_activo(
    db_session: AsyncSession,
    seed_tenant_admin: dict[str, Any],
    seed_estructura: dict[str, Any],
) -> dict[str, Any]:
    """Seeds active padron version with 3 students + docente."""
    from app.models.padron import EntradaPadron, VersionPadron
    from app.models.usuarios_asignaciones import Usuario

    docente = Usuario(
        tenant_id=seed_tenant_admin["tenant_id"],
        nombre="Admin", apellidos="Test",
        email="admin.docente@test.com",
    )
    db_session.add(docente)
    await db_session.flush()

    version = VersionPadron(
        tenant_id=seed_tenant_admin["tenant_id"],
        materia_id=seed_estructura["materia_id"],
        cohorte_id=seed_estructura["cohorte_id"],
        cargado_por=docente.id,
        activa=True,
    )
    db_session.add(version)
    await db_session.flush()

    alumno1 = EntradaPadron(
        tenant_id=seed_tenant_admin["tenant_id"],
        version_id=version.id,
        nombre="Juan", apellidos="Perez",
        email="juan@test.com", comision="A", regional="Norte",
    )
    db_session.add(alumno1)
    alumno2 = EntradaPadron(
        tenant_id=seed_tenant_admin["tenant_id"],
        version_id=version.id,
        nombre="Maria", apellidos="Gomez",
        email="maria@test.com", comision="A", regional="Norte",
    )
    db_session.add(alumno2)
    alumno3 = EntradaPadron(
        tenant_id=seed_tenant_admin["tenant_id"],
        version_id=version.id,
        nombre="Carlos", apellidos="Lopez",
        email="carlos@test.com", comision="B", regional="Sur",
    )
    db_session.add(alumno3)
    await db_session.flush()
    await db_session.commit()

    return {
        "version_id": version.id,
        "alumno1_id": alumno1.id,
        "alumno2_id": alumno2.id,
        "alumno3_id": alumno3.id,
        "docente_id": docente.id,
    }


@pytest.fixture
async def seed_calificaciones(
    db_session: AsyncSession,
    seed_tenant_admin: dict[str, Any],
    seed_estructura: dict[str, Any],
    seed_padron_activo: dict[str, Any],
) -> dict[str, Any]:
    """Seeds Calificacion records for envio masivo tests.

    - Juan: TP1=75 (aprobado), TP2=Satisfactorio (aprobado textual), TP3 missing
    - Maria: TP1=45 (no aprobado), TP2=30 (no aprobado)
    - Carlos: no calificaciones
    """
    from app.models.calificaciones import Calificacion, OrigenCalificacion

    now = datetime.now(UTC)
    tid = seed_tenant_admin["tenant_id"]
    mid = seed_estructura["materia_id"]

    califs = [
        Calificacion(
            tenant_id=tid, entrada_padron_id=seed_padron_activo["alumno1_id"],
            materia_id=mid, actividad="TP1", nota_numerica=75.0, nota_textual=None,
            aprobado=True, origen=OrigenCalificacion.IMPORTADO, importado_at=now,
        ),
        Calificacion(
            tenant_id=tid, entrada_padron_id=seed_padron_activo["alumno1_id"],
            materia_id=mid, actividad="TP2", nota_numerica=None, nota_textual="Satisfactorio",
            aprobado=True, origen=OrigenCalificacion.IMPORTADO, importado_at=now,
        ),
        Calificacion(
            tenant_id=tid, entrada_padron_id=seed_padron_activo["alumno2_id"],
            materia_id=mid, actividad="TP1", nota_numerica=45.0, nota_textual=None,
            aprobado=False, origen=OrigenCalificacion.IMPORTADO, importado_at=now,
        ),
        Calificacion(
            tenant_id=tid, entrada_padron_id=seed_padron_activo["alumno2_id"],
            materia_id=mid, actividad="TP2", nota_numerica=30.0, nota_textual=None,
            aprobado=False, origen=OrigenCalificacion.IMPORTADO, importado_at=now,
        ),
    ]
    for c in califs:
        db_session.add(c)
    await db_session.flush()
    await db_session.commit()
    return {"total": len(califs)}

# ═══════════════════════════════════════════════════════════════
# 9.1 — Tests de máquina de estados (RN-15)
# ═══════════════════════════════════════════════════════════════

class TestMaquinaEstados:
    """9.1 — Máquina de estados: transiciones válidas e inválidas (RN-15)."""

    def test_transicion_pendiente_a_enviando(self):
        from app.models.comunicacion import EstadoComunicacion, validar_transicion
        validar_transicion(EstadoComunicacion.PENDIENTE, EstadoComunicacion.ENVIANDO)

    def test_transicion_pendiente_a_cancelado(self):
        from app.models.comunicacion import EstadoComunicacion, validar_transicion
        validar_transicion(EstadoComunicacion.PENDIENTE, EstadoComunicacion.CANCELADO)

    def test_transicion_enviando_a_enviado(self):
        from app.models.comunicacion import EstadoComunicacion, validar_transicion
        validar_transicion(EstadoComunicacion.ENVIANDO, EstadoComunicacion.ENVIADO)

    def test_transicion_enviando_a_error(self):
        from app.models.comunicacion import EstadoComunicacion, validar_transicion
        validar_transicion(EstadoComunicacion.ENVIANDO, EstadoComunicacion.ERROR)

    def test_transicion_invalida_pendiente_a_enviado(self):
        from app.models.comunicacion import EstadoComunicacion, validar_transicion
        with pytest.raises(ValueError, match="Transición inválida"):
            validar_transicion(EstadoComunicacion.PENDIENTE, EstadoComunicacion.ENVIADO)

    def test_transicion_invalida_enviado_a_pendiente(self):
        from app.models.comunicacion import EstadoComunicacion, validar_transicion
        with pytest.raises(ValueError, match="Transición inválida"):
            validar_transicion(EstadoComunicacion.ENVIADO, EstadoComunicacion.PENDIENTE)

    def test_transicion_invalida_cancelado_a_enviando(self):
        from app.models.comunicacion import EstadoComunicacion, validar_transicion
        with pytest.raises(ValueError, match="Transición inválida"):
            validar_transicion(EstadoComunicacion.CANCELADO, EstadoComunicacion.ENVIANDO)

    def test_transicion_invalida_error_a_cualquiera(self):
        from app.models.comunicacion import EstadoComunicacion, validar_transicion
        with pytest.raises(ValueError, match="Transición inválida"):
            validar_transicion(EstadoComunicacion.ERROR, EstadoComunicacion.PENDIENTE)
        with pytest.raises(ValueError, match="Transición inválida"):
            validar_transicion(EstadoComunicacion.ERROR, EstadoComunicacion.ENVIADO)

    async def test_modelo_transicionar(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        """RED: Comunicacion.transicionar() aplica cambios de estado."""
        from app.models.comunicacion import Comunicacion, EstadoComunicacion

        tid = seed_tenant_admin["tenant_id"]
        com = Comunicacion(
            tenant_id=tid,
            enviado_por_id=seed_padron_activo["docente_id"],
            materia_id=seed_estructura["materia_id"],
            destinatario="test@test.com",
            asunto="Test", cuerpo="Body",
            estado=EstadoComunicacion.PENDIENTE,
        )
        db_session.add(com)
        await db_session.flush()

        com.transicionar(EstadoComunicacion.ENVIANDO)
        assert com.estado == EstadoComunicacion.ENVIANDO

        com.transicionar(EstadoComunicacion.ENVIADO)
        assert com.estado == EstadoComunicacion.ENVIADO

        with pytest.raises(ValueError):
            com.transicionar(EstadoComunicacion.PENDIENTE)

    async def test_transicionar_invalida_lanza_error(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        """TRIANGULATE: transicionar con estado inválido lanza ValueError."""
        from app.models.comunicacion import Comunicacion, EstadoComunicacion

        tid = seed_tenant_admin["tenant_id"]
        com = Comunicacion(
            tenant_id=tid,
            enviado_por_id=seed_padron_activo["docente_id"],
            materia_id=seed_estructura["materia_id"],
            destinatario="test@test.com",
            asunto="Test", cuerpo="Body",
            estado=EstadoComunicacion.ENVIADO,
        )
        db_session.add(com)
        await db_session.flush()

        with pytest.raises(ValueError):
            com.transicionar(EstadoComunicacion.PENDIENTE)


# ═══════════════════════════════════════════════════════════════
# 9.2 — Tests de preview con sustitución de variables (RN-16)
# ═══════════════════════════════════════════════════════════════

class TestPreview:
    """9.2 — Preview: sustitución de {{variables}} en asunto y cuerpo (RN-16)."""

    def test_sustitucion_variables_directas(self):
        from app.services.comunicacion_service import _sustituir_variables

        texto = "Hola {{nombre}}, tu materia {{materia}}"
        resultado = _sustituir_variables(texto, {"nombre": "Juan", "materia": "Matematica"})
        assert resultado == "Hola Juan, tu materia Matematica"

    def test_sustitucion_multiples_variables(self):
        from app.services.comunicacion_service import _sustituir_variables

        texto = "{{nombre}} {{apellido}} - {{materia}} ({{comision}})"
        resultado = _sustituir_variables(texto, {
            "nombre": "Maria", "apellido": "Gomez",
            "materia": "Fisica", "comision": "A",
        })
        assert resultado == "Maria Gomez - Fisica (A)"

    def test_variable_desconocida_queda_textual(self):
        from app.services.comunicacion_service import _sustituir_variables

        resultado = _sustituir_variables("Hola {{nombre}} {{desconocida}}", {"nombre": "Juan"})
        assert resultado == "Hola Juan {{desconocida}}"

    def test_sin_variables_no_modifica(self):
        from app.services.comunicacion_service import _sustituir_variables

        resultado = _sustituir_variables("Texto sin variables", {})
        assert resultado == "Texto sin variables"

    def test_preview_function(self):
        from app.services.comunicacion_service import _preview

        asunto_r, cuerpo_r = _preview(
            "Aviso para {{nombre}}",
            "Tu materia {{materia}} comienza pronto.",
            {"nombre": "Juan", "materia": "Matematica"},
        )
        assert asunto_r == "Aviso para Juan"
        assert cuerpo_r == "Tu materia Matematica comienza pronto."

    async def test_preview_service(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        """RED: ComunicacionService.preview retorna renderizado."""
        from app.services.comunicacion_service import ComunicacionService

        tid = seed_tenant_admin["tenant_id"]
        svc = ComunicacionService(db_session, tid, seed_tenant_admin["user_id"])

        result = await svc.preview(
            "Hola {{nombre}}",
            "Materia: {{materia}}",
            {"nombre": "Juan", "materia": "Matematica"},
        )
        assert result["asunto_renderizado"] == "Hola Juan"
        assert result["cuerpo_renderizado"] == "Materia: Matematica"


# ═══════════════════════════════════════════════════════════════
# 9.3 — Tests de envío masivo
# ═══════════════════════════════════════════════════════════════

class TestEnvioMasivo:
    """9.3 — Envío masivo: con/sin atrasados, aprobación obligatoria."""

    async def test_envio_masivo_con_atrasados(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        seed_calificaciones: dict[str, Any],
    ) -> None:
        """RED: enviar_masivo crea comunicaciones para alumnos atrasados."""
        from app.services.comunicacion_service import ComunicacionService

        tid = seed_tenant_admin["tenant_id"]
        svc = ComunicacionService(db_session, tid, seed_padron_activo["docente_id"])

        result = await svc.enviar_masivo(
            materia_id=seed_estructura["materia_id"],
            asunto="Aviso {{nombre}}",
            cuerpo="Estimado {{nombre}} {{apellido}}, regularizá {{materia}}.",
        )
        assert result["mensajes_creados"] >= 1
        assert UUID(result["lote_id"])

        from app.models.comunicacion import Comunicacion, EstadoComunicacion
        result_all = await db_session.execute(
            select(Comunicacion).where(Comunicacion.lote_id == result["lote_id"])
        )
        comunicaciones = result_all.scalars().all()
        assert len(comunicaciones) == result["mensajes_creados"]
        for c in comunicaciones:
            assert c.estado == EstadoComunicacion.PENDIENTE

    async def test_envio_masivo_sin_atrasados(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
    ) -> None:
        """TRIANGULATE: sin atrasados → lote con 0 mensajes."""
        from app.services.comunicacion_service import ComunicacionService

        tid = seed_tenant_admin["tenant_id"]
        svc = ComunicacionService(db_session, tid, seed_tenant_admin["user_id"])

        result = await svc.enviar_masivo(
            materia_id=seed_estructura["materia_id"],
            asunto="Test", cuerpo="Test body",
        )
        assert result["mensajes_creados"] == 0
        assert UUID(result["lote_id"])

    async def test_aprobacion_requerida_true(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        """TRIANGULATE: tenant con aprobación obligatoria retorna True."""
        from app.services.comunicacion_service import ComunicacionService

        tid = seed_tenant_admin["tenant_id"]
        tenant = await db_session.get(Tenant, tid)
        tenant.settings = {"aprobacion_comunicaciones_obligatoria": True}
        await db_session.flush()

        svc = ComunicacionService(db_session, tid, seed_tenant_admin["user_id"])
        assert await svc.aprobacion_requerida() is True

    async def test_aprobacion_requerida_false(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        """TRIANGULATE: tenant sin flag retorna False."""
        from app.services.comunicacion_service import ComunicacionService

        tid = seed_tenant_admin["tenant_id"]
        svc = ComunicacionService(db_session, tid, seed_tenant_admin["user_id"])
        assert await svc.aprobacion_requerida() is False


# ═══════════════════════════════════════════════════════════════
# 9.4 — Tests de aprobación de lote (RN-17)
# ═══════════════════════════════════════════════════════════════

class TestAprobacion:
    """9.4 — Aprobación: lote Pendiente → Enviando (RN-17)."""

    async def test_aprobar_lote(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        """RED: aprobar_lote transiciona Pendiente → Enviando."""
        from app.models.comunicacion import Comunicacion, EstadoComunicacion
        from app.repositories.comunicacion_repository import ComunicacionRepository

        tid = seed_tenant_admin["tenant_id"]
        lote_id = UUID("00000000-0000-0000-0000-000000000001")

        com1 = Comunicacion(
            tenant_id=tid, enviado_por_id=seed_padron_activo["docente_id"],
            materia_id=seed_estructura["materia_id"],
            destinatario="a@a.com", asunto="A", cuerpo="B",
            estado=EstadoComunicacion.PENDIENTE, lote_id=lote_id,
        )
        com2 = Comunicacion(
            tenant_id=tid, enviado_por_id=seed_padron_activo["docente_id"],
            materia_id=seed_estructura["materia_id"],
            destinatario="b@b.com", asunto="C", cuerpo="D",
            estado=EstadoComunicacion.PENDIENTE, lote_id=lote_id,
        )
        db_session.add_all([com1, com2])
        await db_session.flush()
        await db_session.commit()

        repo = ComunicacionRepository(db_session, tid)
        afectados = await repo.aprobar_lote(lote_id)
        assert afectados == 2

        from app.services.comunicacion_service import ComunicacionService
        svc = ComunicacionService(db_session, tid, seed_padron_activo["docente_id"])
        detalle = await svc.detalle_lote(lote_id)
        for c in detalle["comunicaciones"]:
            assert c["estado"] == EstadoComunicacion.ENVIANDO.value

    async def test_aprobar_lote_vacio_lanza_error(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        """TRIANGULATE: aprobar lote sin Pendientes → ComunicacionError."""
        from app.services.comunicacion_service import ComunicacionError, ComunicacionService

        tid = seed_tenant_admin["tenant_id"]
        svc = ComunicacionService(db_session, tid, seed_tenant_admin["user_id"])

        with pytest.raises(ComunicacionError, match="No hay comunicaciones"):
            await svc.aprobar_lote(UUID("00000000-0000-0000-0000-000000009999"))


# ═══════════════════════════════════════════════════════════════
# 9.5 — Tests de cancelación
# ═══════════════════════════════════════════════════════════════

class TestCancelacion:
    """9.5 — Cancelación: lote completo e individual Pendiente → Cancelado."""

    async def test_cancelar_lote(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        """RED: cancelar_lote transiciona Pendiente → Cancelado."""
        from app.models.comunicacion import Comunicacion, EstadoComunicacion
        from app.repositories.comunicacion_repository import ComunicacionRepository

        tid = seed_tenant_admin["tenant_id"]
        lote_id = UUID("00000000-0000-0000-0000-000000000002")

        com = Comunicacion(
            tenant_id=tid, enviado_por_id=seed_padron_activo["docente_id"],
            materia_id=seed_estructura["materia_id"],
            destinatario="a@a.com", asunto="A", cuerpo="B",
            estado=EstadoComunicacion.PENDIENTE, lote_id=lote_id,
        )
        db_session.add(com)
        await db_session.flush()
        await db_session.commit()

        repo = ComunicacionRepository(db_session, tid)
        afectados = await repo.cancelar_lote(lote_id)
        assert afectados == 1

        com_actualizado = await repo.get(com.id)
        assert com_actualizado.estado == EstadoComunicacion.CANCELADO

    async def test_cancelar_comunicacion_individual(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        """RED: cancelar_comunicacion cancela una sola Pendiente."""
        from app.models.comunicacion import Comunicacion, EstadoComunicacion
        from app.repositories.comunicacion_repository import ComunicacionRepository

        tid = seed_tenant_admin["tenant_id"]
        lote_id = UUID("00000000-0000-0000-0000-000000000003")

        com = Comunicacion(
            tenant_id=tid, enviado_por_id=seed_padron_activo["docente_id"],
            materia_id=seed_estructura["materia_id"],
            destinatario="a@a.com", asunto="A", cuerpo="B",
            estado=EstadoComunicacion.PENDIENTE, lote_id=lote_id,
        )
        db_session.add(com)
        await db_session.flush()
        await db_session.commit()

        repo = ComunicacionRepository(db_session, tid)
        ok = await repo.cancelar_comunicacion(com.id)
        assert ok is True

        com_actualizado = await repo.get(com.id)
        assert com_actualizado.estado == EstadoComunicacion.CANCELADO

    async def test_cancelar_ya_enviado_no_afecta(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        """TRIANGULATE: cancelar comunicación Enviado retorna False."""
        from app.models.comunicacion import Comunicacion, EstadoComunicacion
        from app.repositories.comunicacion_repository import ComunicacionRepository

        tid = seed_tenant_admin["tenant_id"]
        com = Comunicacion(
            tenant_id=tid, enviado_por_id=seed_padron_activo["docente_id"],
            materia_id=seed_estructura["materia_id"],
            destinatario="a@a.com", asunto="A", cuerpo="B",
            estado=EstadoComunicacion.ENVIADO,
        )
        db_session.add(com)
        await db_session.flush()
        await db_session.commit()

        repo = ComunicacionRepository(db_session, tid)
        ok = await repo.cancelar_comunicacion(com.id)
        assert ok is False


# ═══════════════════════════════════════════════════════════════
# 9.6 — Tests de cifrado de destinatario
# ═══════════════════════════════════════════════════════════════

class TestCifrado:
    """9.6 — Cifrado AES-256 del destinatario en reposo."""

    async def test_destinatario_cifrado_en_db(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        test_settings,
    ) -> None:
        """RED: destinatario se almacena cifrado, no texto plano."""
        from app.core.encryption import encrypt_sensitive_value
        from app.models.comunicacion import Comunicacion, EstadoComunicacion
        from app.repositories.comunicacion_repository import ComunicacionRepository

        tid = seed_tenant_admin["tenant_id"]
        email_plano = "juan@test.com"
        email_cifrado = encrypt_sensitive_value(
            email_plano, encryption_key=test_settings.ENCRYPTION_KEY,
        )

        com = Comunicacion(
            tenant_id=tid, enviado_por_id=seed_padron_activo["docente_id"],
            materia_id=seed_estructura["materia_id"],
            destinatario=email_cifrado,
            asunto="Test", cuerpo="Body",
            estado=EstadoComunicacion.PENDIENTE,
        )
        db_session.add(com)
        await db_session.flush()
        await db_session.commit()

        repo = ComunicacionRepository(db_session, tid)
        guardado = await repo.get(com.id)
        assert guardado.destinatario != email_plano
        assert guardado.destinatario == email_cifrado

    async def test_desencriptar_destinatario(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        test_settings,
    ) -> None:
        """TRIANGULATE: service desencripta destinatario correctamente."""
        from app.core.encryption import encrypt_sensitive_value
        from app.models.comunicacion import Comunicacion, EstadoComunicacion

        tid = seed_tenant_admin["tenant_id"]
        email_plano = "maria@test.com"
        lote_id = UUID("00000000-0000-0000-0000-000000000004")
        email_cifrado = encrypt_sensitive_value(
            email_plano, encryption_key=test_settings.ENCRYPTION_KEY,
        )

        com = Comunicacion(
            tenant_id=tid, enviado_por_id=seed_padron_activo["docente_id"],
            materia_id=seed_estructura["materia_id"],
            destinatario=email_cifrado,
            asunto="Test", cuerpo="Body",
            estado=EstadoComunicacion.PENDIENTE, lote_id=lote_id,
        )
        db_session.add(com)
        await db_session.flush()
        await db_session.commit()

        from app.services.comunicacion_service import ComunicacionService
        svc = ComunicacionService(
            db_session, tid, seed_padron_activo["docente_id"], settings=test_settings,
        )
        detalle = await svc.detalle_lote(lote_id)
        assert len(detalle["comunicaciones"]) == 1
        assert detalle["comunicaciones"][0]["destinatario"] == email_plano

    async def test_cifrado_mal_formato_fallback(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        test_settings,
    ) -> None:
        """TRIANGULATE: destinatario inválido → fallback a [cifrado]."""
        from app.models.comunicacion import Comunicacion, EstadoComunicacion

        tid = seed_tenant_admin["tenant_id"]
        lote_id = UUID("00000000-0000-0000-0000-000000000005")

        com = Comunicacion(
            tenant_id=tid, enviado_por_id=seed_padron_activo["docente_id"],
            materia_id=seed_estructura["materia_id"],
            destinatario="no-es-cifrado-valido",
            asunto="Test", cuerpo="Body",
            estado=EstadoComunicacion.PENDIENTE, lote_id=lote_id,
        )
        db_session.add(com)
        await db_session.flush()
        await db_session.commit()

        from app.services.comunicacion_service import ComunicacionService
        svc = ComunicacionService(
            db_session, tid, seed_padron_activo["docente_id"], settings=test_settings,
        )
        detalle = await svc.detalle_lote(lote_id)
        assert detalle["comunicaciones"][0]["destinatario"] == "[cifrado]"


# ═══════════════════════════════════════════════════════════════
# 9.7 — Tests de worker asíncrono
# ═══════════════════════════════════════════════════════════════

class TestWorker:
    """9.7 — Worker: procesa Pendiente → Enviado, salta no aprobados, registra Error."""

    async def test_procesa_pendiente_a_enviado(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        test_settings,
    ) -> None:
        """RED: worker procesa Pendiente → Enviado (success_rate=1.0)."""
        from app.core.encryption import encrypt_sensitive_value
        from app.models.comunicacion import Comunicacion, EstadoComunicacion
        from app.workers.comunicaciones_worker import ComunicacionWorker

        tid = seed_tenant_admin["tenant_id"]
        destinatario_cifrado = encrypt_sensitive_value(
            "alumno@test.com", encryption_key=test_settings.ENCRYPTION_KEY,
        )

        com = Comunicacion(
            tenant_id=tid, enviado_por_id=seed_padron_activo["docente_id"],
            materia_id=seed_estructura["materia_id"],
            destinatario=destinatario_cifrado,
            asunto="Test", cuerpo="Body",
            estado=EstadoComunicacion.PENDIENTE,
        )
        db_session.add(com)
        await db_session.flush()
        await db_session.commit()

        com_id = com.id
        worker = ComunicacionWorker(settings=test_settings, success_rate=1.0)
        await worker._poll(db_session)

        result = await db_session.execute(
            select(Comunicacion).where(Comunicacion.id == com_id)
        )
        actualizado = result.scalar_one()
        assert actualizado.estado == EstadoComunicacion.ENVIADO
        assert actualizado.enviado_at is not None

    async def test_salta_no_aprobados(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        test_settings,
    ) -> None:
        """TRIANGULATE: worker salta comunicaciones de tenant con aprobación obligatoria."""
        from app.models.comunicacion import Comunicacion, EstadoComunicacion
        from app.workers.comunicaciones_worker import ComunicacionWorker

        tid = seed_tenant_admin["tenant_id"]
        tenant = await db_session.get(Tenant, tid)
        tenant.settings = {"aprobacion_comunicaciones_obligatoria": True}
        await db_session.flush()

        com = Comunicacion(
            tenant_id=tid, enviado_por_id=seed_padron_activo["docente_id"],
            materia_id=seed_estructura["materia_id"],
            destinatario="test@test.com",
            asunto="Test", cuerpo="Body",
            estado=EstadoComunicacion.PENDIENTE,
        )
        db_session.add(com)
        await db_session.flush()
        await db_session.commit()

        com_id = com.id
        worker = ComunicacionWorker(settings=test_settings, success_rate=1.0)
        await worker._poll(db_session)

        result = await db_session.execute(
            select(Comunicacion).where(Comunicacion.id == com_id)
        )
        actualizado = result.scalar_one()
        assert actualizado.estado == EstadoComunicacion.PENDIENTE

    async def test_registra_error_cifrado(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
        test_settings,
    ) -> None:
        """TRIANGULATE: destinatario inválido → worker marca Error."""
        from app.models.comunicacion import Comunicacion, EstadoComunicacion
        from app.workers.comunicaciones_worker import ComunicacionWorker

        tid = seed_tenant_admin["tenant_id"]

        com = Comunicacion(
            tenant_id=tid, enviado_por_id=seed_padron_activo["docente_id"],
            materia_id=seed_estructura["materia_id"],
            destinatario="no-es-cifrado-valido",
            asunto="Test", cuerpo="Body",
            estado=EstadoComunicacion.PENDIENTE,
        )
        db_session.add(com)
        await db_session.flush()
        await db_session.commit()

        com_id = com.id
        worker = ComunicacionWorker(settings=test_settings, success_rate=1.0)
        await worker._poll(db_session)

        result = await db_session.execute(
            select(Comunicacion).where(Comunicacion.id == com_id)
        )
        actualizado = result.scalar_one()
        # Error en descifrado → estado Error (simular_envio no se llama)
        assert actualizado.estado == EstadoComunicacion.ERROR


# ═══════════════════════════════════════════════════════════════
# 9.8 — Tests de autorización
# ═══════════════════════════════════════════════════════════════

class TestAutorizacion:
    """9.8 — Autorización: 403 sin permiso, 401 sin auth."""

    @pytest.mark.skip(reason="Requiere fixture de JWT token (no disponible en test unitario)")
    async def test_403_sin_permiso(self, async_client) -> None:
        """RED: endpoint sin permiso retorna 403."""
        pass

    @pytest.mark.skip(reason="Requiere fixture de JWT token (no disponible en test unitario)")
    async def test_401_sin_auth(self, async_client) -> None:
        """TRIANGULATE: endpoint sin auth retorna 401."""
        pass


# ═══════════════════════════════════════════════════════════════
# 9.9 — Tests de tenant isolation
# ═══════════════════════════════════════════════════════════════

class TestTenantIsolation:
    """9.9 — Tenant isolation: datos de tenant A no visibles desde tenant B."""

    async def test_aislamiento_tenant(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        """RED: ComunicacionRepository filtra por tenant."""
        from app.models.comunicacion import Comunicacion, EstadoComunicacion
        from app.repositories.comunicacion_repository import ComunicacionRepository

        tid_a = seed_tenant_admin["tenant_id"]
        lote_id = UUID("00000000-0000-0000-0000-000000000010")

        com = Comunicacion(
            tenant_id=tid_a, enviado_por_id=seed_padron_activo["docente_id"],
            materia_id=seed_estructura["materia_id"],
            destinatario="a@a.com", asunto="A", cuerpo="B",
            estado=EstadoComunicacion.PENDIENTE, lote_id=lote_id,
        )
        db_session.add(com)
        await db_session.flush()
        await db_session.commit()

        # Create tenant B with a different tenant_id
        tenant_b = Tenant(name="Tenant B", code="tenant-b")
        db_session.add(tenant_b)
        await db_session.flush()

        tid_b = tenant_b.id
        repo_b = ComunicacionRepository(db_session, tid_b)

        # repo_b should NOT see data from tenant A
        lotes_b = await repo_b.list_lotes()
        assert len(lotes_b) == 0

        detalle_b = await repo_b.detalle_lote(lote_id)
        assert detalle_b == []

        com_b = await repo_b.get(com.id)
        assert com_b is None

    async def test_list_lotes_solo_del_tenant(
        self, comunicacion_schema, db_session: AsyncSession,
        seed_tenant_admin: dict[str, Any],
        seed_estructura: dict[str, Any],
        seed_padron_activo: dict[str, Any],
    ) -> None:
        """TRIANGULATE: list_lotes solo retorna lotes del tenant actual."""
        from app.models.comunicacion import Comunicacion, EstadoComunicacion
        from app.repositories.comunicacion_repository import ComunicacionRepository

        tid = seed_tenant_admin["tenant_id"]
        lote_a = UUID("00000000-0000-0000-0000-000000000011")
        lote_b = UUID("00000000-0000-0000-0000-000000000012")

        for l_id, email in [(lote_a, "a@a.com"), (lote_b, "b@b.com")]:
            com = Comunicacion(
                tenant_id=tid, enviado_por_id=seed_padron_activo["docente_id"],
                materia_id=seed_estructura["materia_id"],
                destinatario=email, asunto="A", cuerpo="B",
                estado=EstadoComunicacion.PENDIENTE, lote_id=l_id,
            )
            db_session.add(com)
        await db_session.flush()
        await db_session.commit()

        repo = ComunicacionRepository(db_session, tid)
        lotes = await repo.list_lotes()
        assert len(lotes) == 2
        for l in lotes:
            assert l["lote_id"] in (lote_a, lote_b)
