"""Verify all seed data sections have data."""
import asyncio, sys
from app.core.config import Settings
from app.core.database import create_engine_from_url, dispose_engine, get_sessionmaker
from sqlalchemy import select, func

async def main():
    settings = Settings()
    connect_args = {}
    if sys.platform == 'win32':
        connect_args['ssl'] = False
    create_engine_from_url(settings.DATABASE_URL, connect_args=connect_args)
    sf = get_sessionmaker()
    async with sf() as s:
        from app.models.tenant import Tenant
        from app.models.estructura_academica import Carrera, Cohorte, Materia
        from app.models.usuarios_asignaciones import Usuario, Asignacion
        from app.models.padron import EntradaPadron
        from app.models.calificaciones import Calificacion
        from app.models.liquidaciones import Liquidacion, Factura
        from app.models.tarea import Tarea, ComentarioTarea
        from app.models.coloquio import Evaluacion, TurnoEvaluacion, ReservaEvaluacion
        from app.models.encuentro import SlotEncuentro, InstanciaEncuentro
        from app.models.guardia import Guardia
        from app.models.aviso import Aviso
        from app.models.comunicacion import Comunicacion
        from app.models.programas import ProgramaMateria, FechaAcademica
        from app.models.audit_log import AuditLog
        from app.models.hilo_mensaje import HiloMensaje
        from app.models.mensaje_interno import MensajeInterno

        tid = '00000000-0000-0000-0000-000000000001'
        models = [
            ('Carreras', Carrera), ('Cohortes', Cohorte), ('Materias', Materia),
            ('Usuarios', Usuario), ('Asignaciones', Asignacion),
            ('EntradasPadron', EntradaPadron), ('Calificaciones', Calificacion),
            ('Liquidaciones', Liquidacion), ('Facturas', Factura),
            ('Tareas', Tarea), ('ComentariosTarea', ComentarioTarea),
            ('Evaluaciones', Evaluacion), ('TurnosEvaluacion', TurnoEvaluacion),
            ('ReservasEvaluacion', ReservaEvaluacion),
            ('SlotsEncuentro', SlotEncuentro), ('InstanciasEncuentro', InstanciaEncuentro),
            ('Guardias', Guardia), ('Avisos', Aviso), ('Comunicaciones', Comunicacion),
            ('ProgramasMateria', ProgramaMateria), ('FechasAcademicas', FechaAcademica),
            ('AuditLog', AuditLog),
        ]
        ok = True
        for name, model in models:
            stmt = select(func.count()).select_from(model)
            if hasattr(model, 'tenant_id'):
                stmt = stmt.where(model.tenant_id == tid)
            cnt = (await s.execute(stmt)).scalar()
            sym = 'OK' if cnt > 0 else 'MISS'
            if cnt == 0:
                ok = False
            print(f'  [{sym}] {name}: {cnt}')

        hilos = (await s.execute(select(func.count()).select_from(HiloMensaje))).scalar()
        msgs = (await s.execute(select(func.count()).select_from(MensajeInterno))).scalar()
        hilos_ok = hilos > 0
        msgs_ok = msgs > 0
        print(f'  [{"OK" if hilos_ok else "MISS"}] HilosMensaje: {hilos}')
        print(f'  [{"OK" if msgs_ok else "MISS"}] MensajesInternos: {msgs}')
        if not hilos_ok or not msgs_ok:
            ok = False
        print()
        print('ALL SECTIONS OK' if ok else 'SOME SECTIONS MISSING')

    await dispose_engine()

asyncio.run(main())
