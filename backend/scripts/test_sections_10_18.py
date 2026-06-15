"""
Standalone test: run sections 10-18 from seed_dev_data.py
to identify where the error occurs.
"""
import asyncio, sys, traceback
from datetime import date, datetime, timedelta, time, timezone
from uuid import UUID

from app.core.config import Settings
from app.core.database import create_engine_from_url, dispose_engine, get_sessionmaker
from app.core.encryption import encrypt_sensitive_value
from app.core.security import hash_password
from sqlalchemy import select

async def main():
    settings = Settings()
    connect_args = {}
    if sys.platform == 'win32':
        connect_args['ssl'] = False
    create_engine_from_url(settings.DATABASE_URL, connect_args=connect_args)
    sf = get_sessionmaker()

    async with sf() as session:
        # First create section 1-9 data
        print("Creating sections 1-9...")

        from app.models.tenant import Tenant
        from app.models.estructura_academica import Carrera, Cohorte, Materia
        from app.models.usuarios_asignaciones import Usuario, Asignacion
        from app.models.auth import AuthUser
        from app.models.padron import VersionPadron, EntradaPadron
        from app.models.calificaciones import Calificacion, UmbralMateria, OrigenCalificacion
        from app.models.liquidaciones import SalarioBase, SalarioPlus, MateriaPlus, Liquidacion, Factura
        from app.models.liquidaciones import EstadoFactura, EstadoLiquidacion, RolLiquidacion, SegmentoLiquidacion
        from app.models.tarea import Tarea, ComentarioTarea, EstadoTarea
        from app.models.coloquio import Evaluacion, TurnoEvaluacion, ReservaEvaluacion, TipoEvaluacion, EstadoEvaluacion, EstadoReserva
        from app.models.encuentro import SlotEncuentro, InstanciaEncuentro, DiaSemana as DiaSemanaEnc, EstadoInstancia
        from app.models.guardia import Guardia, DiaSemana as DiaSemanaGuardia, EstadoGuardia
        from app.models.aviso import Aviso, AlcanceAviso, SeveridadAviso
        from app.models.comunicacion import Comunicacion, EstadoComunicacion
        from app.models.programas import ProgramaMateria, FechaAcademica, TipoFechaAcademica
        from app.models.audit_log import AuditLog
        from app.models.hilo_mensaje import HiloMensaje
        from app.models.mensaje_interno import MensajeInterno

        TENANT_SEED_UUID = UUID("00000000-0000-0000-0000-000000000001")
        PASSWORD = "test123"

        tenant = await session.get(Tenant, TENANT_SEED_UUID)
        print(f"  Tenant: {tenant.name}")

        # Create minimal section 1-9 data
        carrera_sistemas = Carrera(tenant_id=TENANT_SEED_UUID, codigo="LIC-SIST", nombre="Licenciatura en Sistemas", estado="activa")
        carrera_contador = Carrera(tenant_id=TENANT_SEED_UUID, codigo="CONT-PUB", nombre="Contador Público", estado="activa")
        session.add_all([carrera_sistemas, carrera_contador])
        await session.flush()

        cohorte_2026_sist = Cohorte(tenant_id=TENANT_SEED_UUID, carrera_id=carrera_sistemas.id, nombre="2026", anio=2026, vig_desde=date(2026, 1, 1), estado="activa")
        cohorte_2026_cont = Cohorte(tenant_id=TENANT_SEED_UUID, carrera_id=carrera_contador.id, nombre="2026", anio=2026, vig_desde=date(2026, 1, 1), estado="activa")
        cohorte_2025_sist = Cohorte(tenant_id=TENANT_SEED_UUID, carrera_id=carrera_sistemas.id, nombre="2025", anio=2025, vig_desde=date(2025, 1, 1), vig_hasta=date(2025, 12, 31), estado="activa")
        session.add_all([cohorte_2026_sist, cohorte_2026_cont, cohorte_2025_sist])
        await session.flush()

        materias_sist = [
            Materia(tenant_id=TENANT_SEED_UUID, codigo="PROG-I", nombre="Programación I", estado="activa"),
            Materia(tenant_id=TENANT_SEED_UUID, codigo="BD-I", nombre="Base de Datos I", estado="activa"),
            Materia(tenant_id=TENANT_SEED_UUID, codigo="REDES", nombre="Redes y Comunicaciones", estado="activa"),
            Materia(tenant_id=TENANT_SEED_UUID, codigo="ING-SW", nombre="Ingeniería de Software", estado="activa"),
        ]
        session.add_all(materias_sist)
        materias_cont = [
            Materia(tenant_id=TENANT_SEED_UUID, codigo="CONT-I", nombre="Contabilidad I", estado="activa"),
            Materia(tenant_id=TENANT_SEED_UUID, codigo="IMP-2026", nombre="Impuestos", estado="activa"),
            Materia(tenant_id=TENANT_SEED_UUID, codigo="AUDIT", nombre="Auditoría", estado="activa"),
        ]
        session.add_all(materias_cont)
        materias_compartidas: list[Materia] = []
        all_materias = materias_sist + materias_cont + materias_compartidas
        await session.flush()

        # Create users
        usuario_map = {}
        auth_user_map = {}
        usuarios_data = [
            ("Carlos", "Gutiérrez", "profesor@test.com", "PROFESOR"),
            ("Martín", "Rodríguez", "coordinador@test.com", "COORDINADOR"),
            ("Laura", "Fernández", "nexo@test.com", "NEXO"),
            ("Roberto", "Pérez", "admin@test.com", "ADMIN"),
            ("Gabriela", "Martínez", "finanzas@test.com", "FINANZAS"),
            ("Fernando", "García", "profesor2@test.com", "PROFESOR"),
            ("María", "López", "tutor@test.com", "TUTOR"),
            ("Ana", "Díaz", "tutor2@test.com", "TUTOR"),
            ("Sofía", "Torres", "profesor3@test.com", "PROFESOR"),
        ]
        for nombre, apellido, email, rol in usuarios_data:
            u = Usuario(
                tenant_id=TENANT_SEED_UUID,
                nombre=nombre,
                apellido=apellido,
                email=email,
                tipo_documento="DNI",
                documento=f"30{hash(email)%100000000:08d}",
                rol=rol,
                activo=True,
            )
            session.add(u)
            await session.flush()
            usuario_map[email] = u.id
            hashed = hash_password(PASSWORD)
            encrypted_dni = encrypt_sensitive_value(f"30{hash(email)%100000000:08d}")
            au = AuthUser(
                tenant_id=TENANT_SEED_UUID,
                usuario_id=u.id,
                email=email,
                password_hash=hashed,
                encrypted_dni=encrypted_dni,
                is_active=True,
            )
            session.add(au)
            await session.flush()
            auth_user_map[email] = au.id

        # Create asignaciones
        for email, materia_list in [
            ("profesor@test.com", [materias_sist[0], materias_sist[1]]),
            ("profesor2@test.com", [materias_sist[2]]),
            ("profesor3@test.com", [materias_cont[0]]),
            ("tutor@test.com", [materias_sist[0], materias_sist[1], materias_sist[2]]),
            ("tutor2@test.com", [materias_cont[0], materias_cont[1]]),
            ("coordinador@test.com", [materias_sist[0]]),
            ("nexo@test.com", all_materias),
        ]:
            for m in materia_list:
                session.add(Asignacion(
                    tenant_id=TENANT_SEED_UUID,
                    usuario_id=usuario_map[email],
                    materia_id=m.id,
                    tipo="profesor" if "profesor" in email else "tutor" if "tutor" in email else "coordinador" if "coordinador" in email else "nexo",
                    rol=email.split("@")[0].upper().replace("2","").replace("3",""),
                ))
        await session.flush()

        # Create some alumnos
        alumno_emails = [f"alumno{i}@test.com" for i in range(1, 11)]
        for email in alumno_emails:
            u = Usuario(
                tenant_id=TENANT_SEED_UUID,
                nombre="Alumno", apellido=email.split("@")[0].capitalize(),
                email=email, tipo_documento="DNI",
                documento=f"40{hash(email)%100000000:08d}",
                rol="ALUMNO", activo=True,
            )
            session.add(u)
            await session.flush()
            usuario_map[email] = u.id

        alumno_data = [(email, materias_sist[0]) for email in alumno_emails[:5]]
        alumno_data += [(email, materias_sist[1]) for email in alumno_emails[5:]]

        print("  Sections 1-9 setup complete")
        print()

        # ================================================================
        # NOW test sections 10-18
        # ================================================================
        print("=== Testing sections 10-18 ===")

        try:
            # --- SECTION 10: TAREAS ---
            print("\n--- Section 10: Tareas ---")
            tarea_specs = [
                ("Revisar trabajos prácticos", "Revisar los TP entregados por los alumnos de Programación I", EstadoTarea.PENDIENTE, "profesor@test.com", "coordinador@test.com", materias_sist[0]),
                ("Preparar material didáctico", "Preparar la clase sobre JOINs en SQL", EstadoTarea.EN_PROGRESO, "profesor2@test.com", "coordinador@test.com", materias_sist[1]),
                ("Actualizar planilla de notas", "Pasar las notas del parcial a la planilla maestra", EstadoTarea.RESUELTA, "tutor@test.com", "coordinador@test.com", materias_sist[0]),
                ("Reunión de equipo docente", "Coordinar reunión con el equipo de Sistemas", EstadoTarea.PENDIENTE, "profesor@test.com", "admin@test.com", None),
                ("Actualizar programa de Contabilidad", "Revisar y actualizar el programa de Contabilidad I", EstadoTarea.CANCELADA, "profesor3@test.com", "coordinador@test.com", materias_cont[0]),
            ]

            tareas_ids = []
            for titulo, descripcion, estado, asignado_email, asig_por_email, materia in tarea_specs:
                t = Tarea(
                    tenant_id=TENANT_SEED_UUID,
                    titulo=titulo,
                    descripcion=descripcion,
                    estado=estado,
                    asignado_a=usuario_map[asignado_email],
                    asignado_por=usuario_map[asig_por_email],
                    materia_id=materia.id if materia else None,
                )
                session.add(t)
                await session.flush()
                tareas_ids.append(t.id)
            print("  Tasks created OK")

            # Add comments
            for texto, autor_email in [
                ("Revisé los primeros 5 TP, están aprobados", "profesor@test.com"),
                ("Completé la revisión de todos los TP del grupo A", "profesor@test.com"),
            ]:
                session.add(ComentarioTarea(
                    tenant_id=TENANT_SEED_UUID,
                    tarea_id=tareas_ids[0],
                    autor_id=usuario_map[autor_email],
                    texto=texto,
                ))
            await session.flush()
            print("  Comments created OK")

            # --- SECTION 11: EVALUACIONES ---
            print("\n--- Section 11: Evaluaciones ---")
            coloquio = Evaluacion(
                tenant_id=TENANT_SEED_UUID,
                materia_id=materias_sist[0].id,
                cohorte_id=cohorte_2026_sist.id,
                tipo=TipoEvaluacion.COLOQUIO,
                instancia="Coloquio Final - Julio 2026",
                estado=EstadoEvaluacion.ACTIVA,
            )
            session.add(coloquio)
            await session.flush()

            turno_coloquio = TurnoEvaluacion(
                tenant_id=TENANT_SEED_UUID,
                evaluacion_id=coloquio.id,
                fecha=date(2026, 7, 15),
                hora_inicio=time(9, 0),
                hora_fin=time(12, 0),
                cupo_maximo=30,
                cupo_restante=20,
            )
            session.add(turno_coloquio)

            eval_parcial = Evaluacion(
                tenant_id=TENANT_SEED_UUID,
                materia_id=materias_sist[1].id,
                cohorte_id=cohorte_2026_sist.id,
                tipo=TipoEvaluacion.PARCIAL,
                instancia="Primer Parcial - Base de Datos I",
                estado=EstadoEvaluacion.CERRADA,
            )
            session.add(eval_parcial)
            await session.flush()

            for alumno_email in alumno_emails[:5]:
                session.add(ReservaEvaluacion(
                    tenant_id=TENANT_SEED_UUID,
                    evaluacion_id=coloquio.id,
                    turno_id=turno_coloquio.id,
                    alumno_id=usuario_map[alumno_email],
                    estado=EstadoReserva.ACTIVA,
                ))
            await session.flush()
            print("  Evaluaciones created OK")

            # --- SECTION 12: ENCUENTROS ---
            print("\n--- Section 12: Encuentros ---")
            asignacion_prof = (await session.execute(
                select(Asignacion).where(
                    Asignacion.tenant_id == TENANT_SEED_UUID,
                    Asignacion.rol == "PROFESOR",
                    Asignacion.materia_id == materias_sist[0].id,
                )
            )).scalars().first()
            print(f"  asignacion_prof: {asignacion_prof.id if asignacion_prof else None}")

            slot = SlotEncuentro(
                tenant_id=TENANT_SEED_UUID,
                asignacion_id=asignacion_prof.id,
                materia_id=materias_sist[0].id,
                titulo="Clase de Programación I - Lunes",
                dia_semana=DiaSemanaEnc.LUNES,
                hora=time(18, 0),
                fecha_inicio=date(2026, 3, 1),
                cant_semanas=16,
                meet_url="https://meet.google.com/abc-defg-hij",
                vig_desde=datetime(2026, 3, 1, tzinfo=timezone.utc),
                vig_hasta=datetime(2026, 7, 1, tzinfo=timezone.utc),
            )
            session.add(slot)
            await session.flush()

            session.add(InstanciaEncuentro(
                tenant_id=TENANT_SEED_UUID,
                slot_id=slot.id,
                materia_id=materias_sist[0].id,
                fecha=date(2026, 6, 15),
                hora=time(18, 0),
                titulo="Clase 24: Repaso general",
                estado=EstadoInstancia.PROGRAMADO,
                meet_url="https://meet.google.com/abc-defg-hij",
            ))
            session.add(InstanciaEncuentro(
                tenant_id=TENANT_SEED_UUID,
                slot_id=slot.id,
                materia_id=materias_sist[0].id,
                fecha=date(2026, 4, 10),
                hora=time(18, 0),
                titulo="Clase 8: Estructuras de control",
                estado=EstadoInstancia.REALIZADO,
                video_url="https://drive.google.com/file/d/xyz",
                comentario="Buena participación de los alumnos",
            ))

            session.add(Guardia(
                tenant_id=TENANT_SEED_UUID,
                asignacion_id=asignacion_prof.id,
                materia_id=materias_sist[0].id,
                carrera_id=carrera_sistemas.id,
                cohorte_id=cohorte_2026_sist.id,
                dia=DiaSemanaGuardia.VIERNES,
                horario="16:00 - 18:00",
                estado=EstadoGuardia.PENDIENTE,
                comentarios="Guardia de consultas previa al parcial",
            ))
            session.add(Guardia(
                tenant_id=TENANT_SEED_UUID,
                asignacion_id=asignacion_prof.id,
                materia_id=materias_sist[1].id,
                carrera_id=carrera_sistemas.id,
                cohorte_id=cohorte_2026_sist.id,
                dia=DiaSemanaGuardia.MARTES,
                horario="14:00 - 16:00",
                estado=EstadoGuardia.REALIZADA,
                comentarios="Asistieron 5 alumnos",
            ))
            await session.flush()
            print("  Encuentros/Guardias created OK")

            # --- SECTION 13: AVISOS ---
            print("\n--- Section 13: Avisos ---")
            for alcance, severidad, titulo, cuerpo, rol_destino, materia_id in [
                (AlcanceAviso.GLOBAL, SeveridadAviso.INFO, "Inscripciones abiertas", "Inscripciones abiertas.", None, None),
                (AlcanceAviso.POR_ROL, SeveridadAviso.ADVERTENCIA, "Cierre de actas próximo", "Cierre 31/07.", "PROFESOR", None),
                (AlcanceAviso.POR_MATERIA, SeveridadAviso.INFO, "Coloquio programado", "Coloquio 15/07.", None, materias_sist[0].id),
                (AlcanceAviso.GLOBAL, SeveridadAviso.CRITICO, "Corte programado", "Fuera de línea 01/07.", None, None),
                (AlcanceAviso.POR_ROL, SeveridadAviso.INFO, "Nueva funcionalidad", "Ya pueden cargar actas.", "TUTOR", None),
            ]:
                session.add(Aviso(
                    tenant_id=TENANT_SEED_UUID,
                    alcance=alcance, severidad=severidad,
                    titulo=titulo, cuerpo=cuerpo,
                    rol_destino=rol_destino, materia_id=materia_id,
                    activo=True,
                    inicio_en=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    fin_en=datetime(2026, 12, 31, tzinfo=timezone.utc),
                    requiere_ack=True,
                ))
            await session.flush()
            print("  Avisos created OK")

            # --- SECTION 14: COMUNICACIONES ---
            print("\n--- Section 14: Comunicaciones ---")
            for enviado_por_email, materia, destinatario, asunto, cuerpo, estado, enviado_at in [
                ("coordinador@test.com", materias_sist[0], "profesor@test.com", "Recordatorio", "Cierre notas", EstadoComunicacion.PENDIENTE, None),
                ("profesor@test.com", materias_sist[0], "alumno1@test.com", "Consulta TP", "Obs pendientes", EstadoComunicacion.ENVIADO, datetime.now(timezone.utc) - timedelta(days=2)),
                ("tutor@test.com", materias_sist[1], "alumno2@test.com", "Inasistencias", "3 inasistencias", EstadoComunicacion.ENVIADO, datetime.now(timezone.utc) - timedelta(days=5)),
                ("admin@test.com", materias_sist[0], "profesor@test.com,profesor2@test.com", "Comunicado", "Planillas 30/06", EstadoComunicacion.PENDIENTE, None),
            ]:
                session.add(Comunicacion(
                    tenant_id=TENANT_SEED_UUID,
                    enviado_por_id=usuario_map[enviado_por_email],
                    materia_id=materia.id,
                    destinatario=destinatario,
                    asunto=asunto, cuerpo=cuerpo,
                    estado=estado, enviado_at=enviado_at,
                ))
            await session.flush()
            print("  Comunicaciones created OK")

            # --- SECTION 15: PROGRAMAS ---
            print("\n--- Section 15: Programas ---")
            for materia in [materias_sist[0], materias_sist[1], materias_cont[0]]:
                session.add(ProgramaMateria(
                    tenant_id=TENANT_SEED_UUID,
                    materia_id=materia.id,
                    carrera_id=carrera_sistemas.id if materia in materias_sist else carrera_contador.id,
                    cohorte_id=cohorte_2026_sist.id if materia in materias_sist else cohorte_2026_cont.id,
                    titulo=f"Programa {materia.nombre} - 2026",
                    referencia_archivo=f"programas/{materia.codigo}_2026.pdf",
                ))
            await session.flush()
            print("  Programas created OK")

            # --- SECTION 16: FECHAS ---
            print("\n--- Section 16: Fechas Academicas ---")
            for materia, cohorte, tipo, numero, fecha, titulo in [
                (materias_sist[0], cohorte_2026_sist, TipoFechaAcademica.PARCIAL, 1, date(2026, 4, 20), "Primer Parcial"),
                (materias_sist[0], cohorte_2026_sist, TipoFechaAcademica.PARCIAL, 2, date(2026, 6, 22), "Segundo Parcial"),
                (materias_sist[0], cohorte_2026_sist, TipoFechaAcademica.TP, 1, date(2026, 5, 15), "TP Integrador"),
                (materias_sist[1], cohorte_2026_sist, TipoFechaAcademica.PARCIAL, 1, date(2026, 4, 25), "Primer Parcial"),
                (materias_sist[1], cohorte_2026_sist, TipoFechaAcademica.COLOQUIO, 1, date(2026, 7, 10), "Coloquio Final"),
            ]:
                NOW = datetime.utcnow()
                PERIODO_ACTUAL = f"{NOW.year}-{NOW.month:02d}"
                session.add(FechaAcademica(
                    tenant_id=TENANT_SEED_UUID,
                    materia_id=materia.id, cohorte_id=cohorte.id,
                    tipo=tipo, numero=numero,
                    periodo=PERIODO_ACTUAL,
                    fecha=fecha, titulo=titulo,
                ))
            await session.flush()
            print("  Fechas created OK")

            # --- SECTION 17: AUDIT LOG ---
            print("\n--- Section 17: Audit Log ---")
            for actor_email, accion, detalle, materia_id in [
                ("admin@test.com", "auth.login", "Inicio de sesion", None),
                ("coordinador@test.com", "calificaciones.importar", "Importacion desde Moodle", materias_sist[0].id),
                ("profesor@test.com", "calificaciones.actualizar", "Actualizacion nota alumno1", materias_sist[0].id),
                ("nexo@test.com", "usuarios.crear", "Creacion nuevo usuario", None),
                ("admin@test.com", "configuracion.actualizar", "Actualizacion config tenant", None),
                ("finanzas@test.com", "liquidaciones.cerrar", "Cierre liquidacion", None),
                ("coordinador@test.com", "materias.asignar", "Asignacion profesor", materias_sist[2].id),
                ("tutor@test.com", "comunicacion.enviar", "Envio comunicacion", materias_sist[1].id),
            ]:
                session.add(AuditLog(
                    tenant_id=TENANT_SEED_UUID,
                    actor_id=auth_user_map[actor_email],
                    materia_id=materia_id,
                    accion=accion,
                    detalle={"mensaje": detalle, "origen": "seed"},
                    filas_afectadas=1,
                    ip="127.0.0.1",
                    user_agent="seed-script/1.0",
                ))
            await session.flush()
            print("  AuditLog created OK")

            # --- SECTION 18: MENSAJES ---
            print("\n--- Section 18: Mensajes Internos ---")
            hilo_1 = HiloMensaje(
                tenant_id=TENANT_SEED_UUID,
                asunto="Revision de planillas de examen",
                participantes_ids=[str(usuario_map["coordinador@test.com"]), str(usuario_map["profesor@test.com"])],
            )
            session.add(hilo_1)
            await session.flush()

            for remitente_email, cuerpo in [
                ("coordinador@test.com", "Carlos, revisa las planillas antes del viernes."),
                ("profesor@test.com", "Si, las tengo casi listas."),
                ("coordinador@test.com", "Perfecto, avisame cuando esten listas."),
            ]:
                session.add(MensajeInterno(
                    hilo_id=hilo_1.id,
                    remitente_id=usuario_map[remitente_email],
                    cuerpo=cuerpo,
                ))

            hilo_2 = HiloMensaje(
                tenant_id=TENANT_SEED_UUID,
                asunto="Novedades cohorte 2026",
                participantes_ids=[str(usuario_map["admin@test.com"]), str(usuario_map["coordinador@test.com"]), str(usuario_map["nexo@test.com"])],
            )
            session.add(hilo_2)
            await session.flush()

            for remitente_email, cuerpo in [
                ("admin@test.com", "Cohorte 2026 cupos completos."),
                ("nexo@test.com", "Confirmado. Gestionando asignaciones."),
            ]:
                session.add(MensajeInterno(
                    hilo_id=hilo_2.id,
                    remitente_id=usuario_map[remitente_email],
                    cuerpo=cuerpo,
                ))

            hilo_1.ultimo_mensaje_at = datetime.now(timezone.utc)
            hilo_2.ultimo_mensaje_at = datetime.now(timezone.utc)
            await session.flush()
            print("  Mensajes created OK")

        except Exception as e:
            print(f"\n\n❌ ERROR in sections 10-18: {type(e).__name__}: {e}")
            traceback.print_exc()
            sys.exit(1)

        # Commit everything
        await session.commit()
        print("\n✅ ALL SECTIONS 10-18 COMMITTED SUCCESSFULLY")

    await dispose_engine()

asyncio.run(main())
