from app import db
from app.models.logistica import Camion
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


def obtener_todos_los_camiones():
    return Camion.query.all()


def obtener_camion_por_id(id_camion):
    return Camion.query.get(id_camion)


def crear_camion(data):
    nuevo = Camion(
        id_camion=data["id_camion"],
        placa=data["placa"],
        marca=data["marca"],
        modelo=data["modelo"],
        capacidad_kg=data["capacidad_kg"],
        estado=data.get("estado", "disponible"),
        kilometraje=data.get("kilometraje", 0),
        id_sede=data.get("id_sede"),
    )
    db.session.add(nuevo)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        # Cubre violaciones de CHECK (estado) y de UNIQUE (placa).
        raise ValueError(f"No se pudo crear el camión: {e.orig}") from e

    return nuevo


def actualizar_camion(id_camion, data):
    camion = Camion.query.get(id_camion)
    if camion is None:
        return None

    # placa es un campo crítico (identificador legal del vehículo):
    # no se toca aunque venga en el body de la petición.
    campos_editables = [
        "marca",
        "modelo",
        "capacidad_kg",
        "estado",
        "kilometraje",
        "id_sede",
    ]
    for campo in campos_editables:
        if campo in data:
            setattr(camion, campo, data[campo])

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"No se pudo actualizar el camión: {e.orig}") from e

    return camion


def tiene_asignaciones_asociadas(id_camion):
    resultado = db.session.execute(
        text("SELECT 1 FROM asignacion_camiones WHERE id_camion = :id LIMIT 1"),
        {"id": id_camion},
    ).first()
    return resultado is not None


def tiene_historial_conductores(id_camion):
    resultado = db.session.execute(
        text("SELECT 1 FROM camion_conductor WHERE id_camion = :id LIMIT 1"),
        {"id": id_camion},
    ).first()
    return resultado is not None


def eliminar_camion(id_camion):
    camion = Camion.query.get(id_camion)
    if camion is None:
        return "no_encontrado"

    if tiene_asignaciones_asociadas(id_camion):
        return "tiene_asignaciones"

    if tiene_historial_conductores(id_camion):
        return "tiene_historial_conductores"

    db.session.delete(camion)
    try:
        db.session.commit()
    except IntegrityError:
        # Red de seguridad por si en el futuro se agrega otra tabla
        # con FK RESTRICT hacia camion y se nos olvida validarla aquí.
        db.session.rollback()
        return "tiene_registros_asociados"

    return "eliminado"
