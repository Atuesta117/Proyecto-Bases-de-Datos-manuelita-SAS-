from app import db
from app.models.logistica import Conductor
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


def obtener_todos_los_conductores():
    return Conductor.query.all()


def obtener_conductor_por_id(id_conductor):
    return Conductor.query.get(id_conductor)


def crear_conductor(data):
    nuevo = Conductor(
        id_conductor=data["id_conductor"],
        nombre=data["nombre"],
        apellido=data["apellido"],
        cedula=data["cedula"],
        telefono=data["telefono"],
        licencia=data["licencia"],
        fecha_vencimiento_licencia=data["fecha_vencimiento_licencia"],
        id_sede=data.get("id_sede"),
        disponible=data.get("disponible", True),
    )
    db.session.add(nuevo)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        # Cubre violaciones de UNIQUE (cedula, licencia).
        raise ValueError(f"No se pudo crear el conductor: {e.orig}") from e

    return nuevo


def actualizar_conductor(id_conductor, data):
    conductor = Conductor.query.get(id_conductor)
    if conductor is None:
        return None

    # cedula es un campo crítico (identidad legal del conductor):
    # no se toca aunque venga en el body de la petición.
    campos_editables = [
        "nombre",
        "apellido",
        "telefono",
        "licencia",
        "fecha_vencimiento_licencia",
        "id_sede",
        "disponible",
    ]
    for campo in campos_editables:
        if campo in data:
            setattr(conductor, campo, data[campo])

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"No se pudo actualizar el conductor: {e.orig}") from e

    return conductor


def tiene_asignaciones_camion(id_conductor):
    resultado = db.session.execute(
        text("SELECT 1 FROM camion_conductor WHERE id_conductor = :id LIMIT 1"),
        {"id": id_conductor},
    ).first()
    return resultado is not None


def eliminar_conductor(id_conductor):
    conductor = Conductor.query.get(id_conductor)
    if conductor is None:
        return "no_encontrado"

    if tiene_asignaciones_camion(id_conductor):
        return "tiene_asignaciones_camion"

    db.session.delete(conductor)
    try:
        db.session.commit()
    except IntegrityError:
        # Red de seguridad por si en el futuro se agrega otra tabla
        # con FK RESTRICT hacia conductor y se nos olvida validarla aquí.
        db.session.rollback()
        return "tiene_registros_asociados"

    return "eliminado"
