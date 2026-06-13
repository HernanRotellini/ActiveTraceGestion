"""Script de seed para datos de desarrollo.

Crea datos de prueba completos para visualizar en el frontend:
carreras, cohortes, materias, usuarios por rol, asignaciones,
padrón de alumnos, calificaciones, grilla salarial y liquidaciones.

Uso:
    docker compose run --rm api python scripts/seed_dev_data.py

Requiere que las migraciones ya se hayan ejecutado (alembic upgrade head).
"""

import asyncio
import sys
from datetime import date, datetime, timedelta
from uuid import UUID, uuid4

# ── Windows event loop fix ───────────────────────────────────────
if sys.platform == "win32":
    import asyncio as _asyncio

    try:
        _asyncio.set_event_loop_policy(_asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

# ── Constantes ───────────────────────────────────────────────────
TENANT_SEED_UUID = UUID("00000000-0000-0000-0000-000000000001")
TENANT_CODE = "UTN_MENDOZA_GLOBAL"
PASSWORD = "test123"  # misma password para todos los usuarios de prueba

ROLES_DOMINIO = ["ALUMNO", "TUTOR", "PROFESOR", "COORDINADOR", "NEXO", "ADMIN", "FINANZAS"]

NOW = datetime.utcnow()
PERIODO_ACTUAL = f"{NOW.year}-{NOW.month:02d}"
PERIODO_ANTERIOR = (
    f"{NOW.year - 1}-{NOW.month + 6:02d}" if NOW.month > 6 else f"{NOW.year - 1}-{NOW.month + 6:02d}"
)

# ── Usuarios de prueba ───────────────────────────────────────────
USUARIOS = [
    # (nombre, apellido, email, rol, facturador, es_alumno)
    ("Carlos", "Gutiérrez", "profesor@test.com", "PROFESOR", False, False),
    ("María", "López", "tutor@test.com", "TUTOR", False, False),
    ("Martín", "Rodríguez", "coordinador@test.com", "COORDINADOR", False, False),
    ("Laura", "Fernández", "nexo@test.com", "NEXO", False, False),
    ("Roberto", "Pérez", "admin@test.com", "ADMIN", False, False),
    ("Gabriela", "Martínez", "finanzas@test.com", "FINANZAS", False, False),
    ("Fernando", "García", "profesor2@test.com", "PROFESOR", True, False),  # facturante
    ("Ana", "Díaz", "tutor2@test.com", "TUTOR", False, False),
    ("Sofía", "Torres", "profesor3@test.com", "PROFESOR", False, False),
    ("Alumno", "Uno", "alumno1@test.com", "ALUMNO", False, True),
    ("Alumno", "Dos", "alumno2@test.com", "ALUMNO", False, True),
    ("Alumno", "Tres", "alumno3@test.com", "ALUMNO", False, True),
    ("Alumno", "Cuatro", "alumno4@test.com", "ALUMNO", False, True),
    ("Alumno", "Cinco", "alumno5@test.com", "ALUMNO", False, True),
    ("Alumno", "Seis", "alumno6@test.com", "ALUMNO", False, True),
    ("Alumno", "Siete", "alumno7@test.com", "ALUMNO", False, True),
    ("Alumno", "Ocho", "alumno8@test.com", "ALUMNO", False, True),
    ("Alumno", "Nueve", "alumno9@test.com", "ALUMNO", False, True),
    ("Alumno", "Diez", "alumno10@test.com", "ALUMNO", False, True),
]


async def main() -> None:
    from app.core.config import Settings
    from app.core.database import Base, create_engine_from_url, dispose_engine, get_sessionmaker
    from app.core.encryption import encrypt_sensitive_value
    from app.core.security import hash_password

    # ── Modelos ──────────────────────────────────────────────────
    from app.models.tenant import Tenant
    from app.models.auth import AuthUser
    from app.models.estructura_academica import Carrera, Cohorte, Materia
    from app.models.usuarios_asignaciones import Usuario, Asignacion
    from app.models.padron import VersionPadron, EntradaPadron
    from app.models.calificaciones import Calificacion, UmbralMateria, OrigenCalificacion
    from app.models.liquidaciones import SalarioBase, SalarioPlus, MateriaPlus, Liquidacion, Factura
    from app.models.liquidaciones import (
        EstadoFactura,
        EstadoLiquidacion,
        RolLiquidacion,
        SegmentoLiquidacion,
    )

    # ── Init engine ──────────────────────────────────────────────
    settings = Settings()  # type: ignore[call-arg]
    connect_args: dict[str, object] = {}
    if sys.platform == "win32":
        connect_args["ssl"] = False
    create_engine_from_url(settings.DATABASE_URL, connect_args=connect_args)
    sessionmaker = get_sessionmaker()

    async with sessionmaker() as session:
        # ── Verificar tenant semilla ─────────────────────────────
        tenant = await session.get(Tenant, TENANT_SEED_UUID)
        if tenant is None:
            print(
                "ERROR: Tenant semilla no encontrado. "
                "¿Ejecutaste 'alembic upgrade head' primero?"
            )
            sys.exit(1)
        print(f"✓ Tenant encontrado: {tenant.name} ({tenant.code})")

        # ── Verificar que no haya datos para evitar duplicados ───
        existing_carreras = await session.execute(
            __import__("sqlalchemy").select(Carrera).where(Carrera.tenant_id == TENANT_SEED_UUID)
        )
        if existing_carreras.scalars().first() is not None:
            print("⚠ Los datos de seed ya existen. Omitiendo creación.")
            print("  Si querés regenerarlos, truncá las tablas primero.")
            await dispose_engine()
            return

        # ================================================================
        # 1. CARRERAS y COHORTES
        # ================================================================
        print("\n── Creando carreras y cohortes ──")
        carrera_sistemas = Carrera(
            tenant_id=TENANT_SEED_UUID,
            codigo="LIC-SIST",
            nombre="Licenciatura en Sistemas",
            estado="activa",
        )
        carrera_contador = Carrera(
            tenant_id=TENANT_SEED_UUID,
            codigo="CONT-PUB",
            nombre="Contador Público",
            estado="activa",
        )
        session.add_all([carrera_sistemas, carrera_contador])
        await session.flush()
        print(f"  ✓ Carreras: {carrera_sistemas.nombre}, {carrera_contador.nombre}")

        cohorte_2026_sist = Cohorte(
            tenant_id=TENANT_SEED_UUID,
            carrera_id=carrera_sistemas.id,
            nombre="2026",
            anio=2026,
            vig_desde=date(2026, 1, 1),
            estado="activa",
        )
        cohorte_2026_cont = Cohorte(
            tenant_id=TENANT_SEED_UUID,
            carrera_id=carrera_contador.id,
            nombre="2026",
            anio=2026,
            vig_desde=date(2026, 1, 1),
            estado="activa",
        )
        cohorte_2025_sist = Cohorte(
            tenant_id=TENANT_SEED_UUID,
            carrera_id=carrera_sistemas.id,
            nombre="2025",
            anio=2025,
            vig_desde=date(2025, 1, 1),
            vig_hasta=date(2025, 12, 31),
            estado="activa",
        )
        session.add_all([cohorte_2026_sist, cohorte_2026_cont, cohorte_2025_sist])
        await session.flush()
        print(f"  ✓ Cohortes: 2026 (Sistemas), 2026 (Contador), 2025 (Sistemas)")

        # ================================================================
        # 2. MATERIAS
        # ================================================================
        print("\n── Creando materias ──")
        materias_sist = [
            Materia(
                tenant_id=TENANT_SEED_UUID,
                codigo="PROG-I",
                nombre="Programación I",
                estado="activa",
            ),
            Materia(
                tenant_id=TENANT_SEED_UUID,
                codigo="BD-I",
                nombre="Base de Datos I",
                estado="activa",
            ),
            Materia(
                tenant_id=TENANT_SEED_UUID,
                codigo="REDES",
                nombre="Redes y Comunicaciones",
                estado="activa",
            ),
            Materia(
                tenant_id=TENANT_SEED_UUID,
                codigo="ING-SW",
                nombre="Ingeniería de Software",
                estado="activa",
            ),
        ]
        materias_cont = [
            Materia(
                tenant_id=TENANT_SEED_UUID,
                codigo="CONT-I",
                nombre="Contabilidad I",
                estado="activa",
            ),
            Materia(
                tenant_id=TENANT_SEED_UUID,
                codigo="IMP-2026",
                nombre="Impuestos",
                estado="activa",
            ),
            Materia(
                tenant_id=TENANT_SEED_UUID,
                codigo="AUDIT",
                nombre="Auditoría",
                estado="activa",
            ),
        ]
        all_materias = materias_sist + materias_cont
        session.add_all(all_materias)
        await session.flush()
        for m in all_materias:
            print(f"  ✓ {m.codigo}: {m.nombre}")

        # ================================================================
        # 3. USUARIOS + AUTH_USERS
        # ================================================================
        print("\n── Creando usuarios ──")
        password_hash = hash_password(PASSWORD)
        usuario_map: dict[str, UUID] = {}  # email -> usuario_id
        auth_user_map: dict[str, UUID] = {}  # email -> auth_user_id

        for nombre, apellido, email, rol, facturador, es_alumno in USUARIOS:
            # Crear Usuario (perfil con PII cifrada)
            usuario = Usuario(
                tenant_id=TENANT_SEED_UUID,
                nombre=nombre,
                apellidos=apellido,
                email=encrypt_sensitive_value(email, encryption_key=settings.ENCRYPTION_KEY),
                email_hash=__import__("hashlib").sha256(email.lower().encode("utf-8")).hexdigest(),
                dni=encrypt_sensitive_value(
                    f"{hash((nombre, apellido, email)) % 100_000_000:08d}",
                    encryption_key=settings.ENCRYPTION_KEY,
                ),
                cuil=encrypt_sensitive_value(
                    f"20-{hash((nombre, apellido, email)) % 100_000_000:08d}-1",
                    encryption_key=settings.ENCRYPTION_KEY,
                ),
                banco=("Banco Nación" if not es_alumno else None),
                cbu=(
                    encrypt_sensitive_value(
                        f"0000000000000000000{hash((nombre, apellido, email)) % 1000:03d}",
                        encryption_key=settings.ENCRYPTION_KEY,
                    )
                    if not es_alumno
                    else None
                ),
                facturador=facturador,
                estado="activo",
            )
            session.add(usuario)
            await session.flush()
            usuario_map[email] = usuario.id

            # Crear AuthUser (login)
            roles_list = [rol] if not es_alumno else ["ALUMNO"]
            auth_user = AuthUser(
                tenant_id=TENANT_SEED_UUID,
                email=email,
                password_hash=password_hash,
                roles=roles_list,
                is_active=True,
            )
            session.add(auth_user)
            await session.flush()
            auth_user_map[email] = auth_user.id

            print(f"  ✓ {rol:12s} → {email}  (usuario_id={str(usuario.id)[:8]}…)")

        # ================================================================
        # 4. ASIGNACIONES
        # ================================================================
        print("\n── Creando asignaciones ──")

        # PROFESORES a materias de Sistemas
        comisiones_sist = ["A", "B"]
        for materia in materias_sist:
            for prof_email in ["profesor@test.com", "profesor2@test.com"]:
                if prof_email in usuario_map:
                    session.add(
                        Asignacion(
                            tenant_id=TENANT_SEED_UUID,
                            usuario_id=usuario_map[prof_email],
                            rol="PROFESOR",
                            materia_id=materia.id,
                            cohorte_id=cohorte_2026_sist.id,
                            comisiones=comisiones_sist,
                            desde=date(2026, 3, 1),
                        )
                    )

        # PROFESOR3 materia extra
        session.add(
            Asignacion(
                tenant_id=TENANT_SEED_UUID,
                usuario_id=usuario_map["profesor3@test.com"],
                rol="PROFESOR",
                materia_id=materias_sist[2].id,  # Redes
                cohorte_id=cohorte_2026_sist.id,
                comisiones=["A"],
                desde=date(2026, 3, 1),
            )
        )

        # PROFESORES a materias de Contador
        for materia in materias_cont:
            for prof_email in ["profesor@test.com", "profesor3@test.com"]:
                if prof_email in usuario_map:
                    session.add(
                        Asignacion(
                            tenant_id=TENANT_SEED_UUID,
                            usuario_id=usuario_map[prof_email],
                            rol="PROFESOR",
                            materia_id=materia.id,
                            cohorte_id=cohorte_2026_cont.id,
                            comisiones=["A"],
                            desde=date(2026, 3, 1),
                        )
                    )

        # TUTORES a materias de Sistemas
        for materia in materias_sist:
            session.add(
                Asignacion(
                    tenant_id=TENANT_SEED_UUID,
                    usuario_id=usuario_map["tutor@test.com"],
                    rol="TUTOR",
                    materia_id=materia.id,
                    cohorte_id=cohorte_2026_sist.id,
                    comisiones=["A", "B"],
                    desde=date(2026, 3, 1),
                )
            )

        # TUTOR2 a materias de Contador
        for materia in materias_cont:
            session.add(
                Asignacion(
                    tenant_id=TENANT_SEED_UUID,
                    usuario_id=usuario_map["tutor2@test.com"],
                    rol="TUTOR",
                    materia_id=materia.id,
                    cohorte_id=cohorte_2026_cont.id,
                    comisiones=["A"],
                    desde=date(2026, 3, 1),
                )
            )

        # COORDINADOR a nivel carrera (sin materia específica)
        session.add(
            Asignacion(
                tenant_id=TENANT_SEED_UUID,
                usuario_id=usuario_map["coordinador@test.com"],
                rol="COORDINADOR",
                carrera_id=carrera_sistemas.id,
                cohorte_id=cohorte_2026_sist.id,
                desde=date(2026, 1, 1),
            )
        )
        session.add(
            Asignacion(
                tenant_id=TENANT_SEED_UUID,
                usuario_id=usuario_map["coordinador@test.com"],
                rol="COORDINADOR",
                carrera_id=carrera_contador.id,
                cohorte_id=cohorte_2026_cont.id,
                desde=date(2026, 1, 1),
            )
        )

        # NEXO
        session.add(
            Asignacion(
                tenant_id=TENANT_SEED_UUID,
                usuario_id=usuario_map["nexo@test.com"],
                rol="NEXO",
                carrera_id=carrera_sistemas.id,
                cohorte_id=cohorte_2026_sist.id,
                desde=date(2026, 1, 1),
            )
        )

        # ADMIN y FINANZAS sin asignaciones específicas (tienen acceso global)

        await session.flush()
        print("  ✓ Asignaciones creadas: PROFESORES, TUTORES, COORDINADOR, NEXO")

        # ================================================================
        # 5. PADRÓN DE ALUMNOS
        # ================================================================
        print("\n── Creando padrón de alumnos ──")
        alumnos_emails = [email for _, _, email, rol, _, _ in USUARIOS if rol == "ALUMNO"]
        alumno_ids = [usuario_map[email] for email in alumnos_emails]
        alumno_data = [
            (nombre, apellido, email)
            for nombre, apellido, email, rol, _, _ in USUARIOS
            if rol == "ALUMNO"
        ]

        for materia in all_materias:
            cohorte_id = cohorte_2026_sist.id if materia in materias_sist else cohorte_2026_cont.id
            comisiones = ["A", "B"] if materia in materias_sist else ["A"]

            # Crear version de padron
            version = VersionPadron(
                tenant_id=TENANT_SEED_UUID,
                materia_id=materia.id,
                cohorte_id=cohorte_id,
                cargado_por=usuario_map["admin@test.com"],
                cargado_at=NOW - timedelta(days=30),
                activa=True,
            )
            session.add(version)
            await session.flush()

            # Crear entradas de padron (alumnos repartidos en comisiones)
            for i, (nombre, apellido, email) in enumerate(alumno_data):
                comision = comisiones[i % len(comisiones)]
                entrada = EntradaPadron(
                    tenant_id=TENANT_SEED_UUID,
                    version_id=version.id,
                    usuario_id=usuario_map[email],
                    nombre=nombre,
                    apellidos=apellido,
                    email=email,
                    comision=comision,
                )
                session.add(entrada)

        await session.flush()
        print(f"  ✓ {len(alumno_data)} alumnos cargados en {len(all_materias)} materias")

        # ================================================================
        # 6. CALIFICACIONES de ejemplo
        # ================================================================
        print("\n── Creando calificaciones de ejemplo ──")
        for materia in all_materias[:3]:  # primeras 3 materias
            cohorte_id = cohorte_2026_sist.id if materia in materias_sist else cohorte_2026_cont.id
            # Buscar entradas de padron para esta materia
            entradas = await session.execute(
                __import__("sqlalchemy").select(EntradaPadron).where(
                    EntradaPadron.tenant_id == TENANT_SEED_UUID,
                    EntradaPadron.version_id.in_(
                        __import__("sqlalchemy").select(VersionPadron.id).where(
                            VersionPadron.tenant_id == TENANT_SEED_UUID,
                            VersionPadron.materia_id == materia.id,
                        )
                    ),
                )
            )
            entradas_list = entradas.scalars().all()
            for i, entrada in enumerate(entradas_list):
                # 70% aprueba, 30% desaprueba
                nota = 7.0 if i % 10 < 7 else 3.0
                session.add(
                    Calificacion(
                        tenant_id=TENANT_SEED_UUID,
                        entrada_padron_id=entrada.id,
                        materia_id=materia.id,
                        actividad="Parcial 1",
                        nota_numerica=nota,
                        aprobado=nota >= 6.0,
                        origen=OrigenCalificacion.IMPORTADO,
                        importado_at=NOW - timedelta(days=15),
                    )
                )
                # Segunda actividad
                nota2 = 8.0 if i % 10 < 6 else 4.0
                session.add(
                    Calificacion(
                        tenant_id=TENANT_SEED_UUID,
                        entrada_padron_id=entrada.id,
                        materia_id=materia.id,
                        actividad="TP Integrador",
                        nota_numerica=nota2,
                        aprobado=nota2 >= 6.0,
                        origen=OrigenCalificacion.IMPORTADO,
                        importado_at=NOW - timedelta(days=5),
                    )
                )

        await session.flush()
        print("  ✓ Calificaciones de ejemplo creadas")

        # ================================================================
        # 7. GRILLA SALARIAL
        # ================================================================
        print("\n── Creando grilla salarial ──")

        bases = [
            SalarioBase(
                tenant_id=TENANT_SEED_UUID,
                rol=RolLiquidacion.PROFESOR,
                monto=150000.00,
                desde=date(2026, 1, 1),
            ),
            SalarioBase(
                tenant_id=TENANT_SEED_UUID,
                rol=RolLiquidacion.TUTOR,
                monto=80000.00,
                desde=date(2026, 1, 1),
            ),
            SalarioBase(
                tenant_id=TENANT_SEED_UUID,
                rol=RolLiquidacion.NEXO,
                monto=100000.00,
                desde=date(2026, 1, 1),
            ),
            SalarioBase(
                tenant_id=TENANT_SEED_UUID,
                rol=RolLiquidacion.COORDINADOR,
                monto=200000.00,
                desde=date(2026, 1, 1),
            ),
        ]
        session.add_all(bases)
        await session.flush()

        pluses = [
            SalarioPlus(
                tenant_id=TENANT_SEED_UUID,
                rol=RolLiquidacion.PROFESOR,
                grupo="PROG",
                descripcion="Plus por materia de Programación",
                monto=15000.00,
                desde=date(2026, 1, 1),
            ),
            SalarioPlus(
                tenant_id=TENANT_SEED_UUID,
                rol=RolLiquidacion.PROFESOR,
                grupo="BD",
                descripcion="Plus por materia de Base de Datos",
                monto=12000.00,
                desde=date(2026, 1, 1),
            ),
            SalarioPlus(
                tenant_id=TENANT_SEED_UUID,
                rol=RolLiquidacion.PROFESOR,
                grupo="REDES",
                descripcion="Plus por materia de Redes",
                monto=10000.00,
                desde=date(2026, 1, 1),
            ),
            SalarioPlus(
                tenant_id=TENANT_SEED_UUID,
                rol=RolLiquidacion.PROFESOR,
                grupo="CONT",
                descripcion="Plus por materia de Contabilidad",
                monto=18000.00,
                desde=date(2026, 1, 1),
            ),
            SalarioPlus(
                tenant_id=TENANT_SEED_UUID,
                rol=RolLiquidacion.PROFESOR,
                grupo="IMP",
                descripcion="Plus por materia de Impuestos",
                monto=20000.00,
                desde=date(2026, 1, 1),
            ),
            SalarioPlus(
                tenant_id=TENANT_SEED_UUID,
                rol=RolLiquidacion.TUTOR,
                grupo="TUT-GRAL",
                descripcion="Plus general de tutoría",
                monto=8000.00,
                desde=date(2026, 1, 1),
            ),
        ]
        session.add_all(pluses)
        await session.flush()

        # Mapeo Materia → Plus (grupo)
        materia_plus_map = {
            "PROG-I": "PROG",
            "BD-I": "BD",
            "REDES": "REDES",
            "CONT-I": "CONT",
            "IMP-2026": "IMP",
        }
        for materia in all_materias:
            grupo = materia_plus_map.get(materia.codigo)
            if grupo:
                session.add(
                    MateriaPlus(
                        tenant_id=TENANT_SEED_UUID,
                        materia_id=materia.id,
                        grupo=grupo,
                        desde=date(2026, 1, 1),
                    )
                )

        await session.flush()
        print("  ✓ Grilla salarial: bases, pluses y mapeo materia→plus")

        # ================================================================
        # 8. LIQUIDACIONES de ejemplo
        # ================================================================
        print("\n── Creando liquidaciones de ejemplo ──")

        # Liquidaciones abiertas para el período actual
        for materia in [materias_sist[0], materias_sist[1], materias_cont[0]]:
            for prof_email in ["profesor@test.com", "profesor3@test.com"]:
                if prof_email not in usuario_map:
                    continue
                monto_base_val = 150000.00
                monto_plus_val = 15000.00
                es_facturante = prof_email == "profesor2@test.com"
                session.add(
                    Liquidacion(
                        tenant_id=TENANT_SEED_UUID,
                        cohorte_id=cohorte_2026_sist.id,
                        usuario_id=usuario_map[prof_email],
                        periodo=PERIODO_ACTUAL,
                        rol=RolLiquidacion.PROFESOR,
                        estado=EstadoLiquidacion.ABIERTA,
                        monto_base=monto_base_val,
                        monto_plus=monto_plus_val,
                        monto_total=monto_base_val + monto_plus_val,
                        comisiones=["A"],
                        es_nexo=False,
                        excluido_por_factura=es_facturante,
                    )
                )

        # Liquidación cerrada para el período anterior
        session.add(
            Liquidacion(
                tenant_id=TENANT_SEED_UUID,
                cohorte_id=cohorte_2025_sist.id,
                usuario_id=usuario_map["profesor@test.com"],
                periodo=PERIODO_ANTERIOR,
                rol=RolLiquidacion.PROFESOR,
                estado=EstadoLiquidacion.CERRADA,
                monto_base=140000.00,
                monto_plus=12000.00,
                monto_total=152000.00,
                comisiones=["A", "B"],
                es_nexo=False,
                excluido_por_factura=False,
            )
        )

        await session.flush()
        print(f"  ✓ Liquidaciones ({PERIODO_ACTUAL}: abiertas, {PERIODO_ANTERIOR}: cerrada)")

        # ================================================================
        # 9. FACTURA de ejemplo
        # ================================================================
        print("\n── Creando factura de ejemplo ──")
        session.add(
            Factura(
                tenant_id=TENANT_SEED_UUID,
                usuario_id=usuario_map["profesor2@test.com"],
                periodo=PERIODO_ACTUAL,
                detalle="Honorarios profesionales - Período " + PERIODO_ACTUAL,
                referencia_archivo="facturas/doc/factura-ejemplo.pdf",
                archivo_size_bytes=102400,
                estado=EstadoFactura.PENDIENTE,
            )
        )
        await session.flush()
        print("  ✓ Factura de ejemplo (profesor facturante)")

        # ================================================================
        # FINAL
        # ================================================================
        await session.commit()
        print("\n" + "=" * 60)
        print("  ✅ SEED COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"\n  Tenant:      {TENANT_CODE}")
        print(f"  Password:    {PASSWORD}")
        print(f"\n  Usuarios creados: {len(USUARIOS)}")
        print(f"  Carreras:        2")
        print(f"  Materias:        {len(all_materias)}")
        print(f"  Alumnos padrón:  {len(alumno_data)}")
        print(f"\n  Ver USUARIOS_DE_PRUEBA.md para credenciales")
        print()

    await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
