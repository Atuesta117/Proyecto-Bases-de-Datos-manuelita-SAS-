from datetime import date

from app import db
from app.models.logistica import AsignacionCamiones, Envio, EnvioInternacional, EnvioNacional
from sqlalchemy.exc import IntegrityError


def obtener_todos_los_envios():
    """Obtiene la lista completa de envíos registrados en el sistema."""
    return Envio.query.all()


def obtener_envio_por_id(id_envio):
    """Busca un envío por su identificador primario."""
    return Envio.query.get(id_envio)


def _obtener_detalle_modelo(envio):
    """Devuelve el detalle específico (nacional o internacional) asociado al envío."""
    if envio.tipo_envio == "nacional":
        return EnvioNacional.query.get(envio.id_envio)
    return EnvioInternacional.query.get(envio.id_envio)


def obtener_detalle_envio(id_envio):
    """Combina la información del envío con su detalle en un diccionario."""
    envio = Envio.query.get(id_envio)
    if envio is None:
        return None

    detalle = _obtener_detalle_modelo(envio)
    resultado = envio.to_dict()
    resultado["detalle"] = detalle.to_dict() if detalle else None
    return resultado


# --- RESTRICCIONES ESTRICTAS (BLOQUEO DE ESCRITURA DIRECTA) ---

def crear_envio(data):
    """Lanza una excepción. Los envíos se crean por flujo interno al confirmar un pedido."""
    raise PermissionError(
        "No está permitido crear envíos de forma manual. "
        "Los envíos se generan automáticamente cuando un pedido es confirmado por el sistema."
    )


def actualizar_envio(id_envio, data):
    """Lanza una excepción. Los envíos son inmutables una vez generados."""
    raise PermissionError(
        f"No se permite modificar el envío '{id_envio}'. "
        "Toda la información es inmutable debido a su asociación con un pedido activo."
    )


def eliminar_envio(id_envio):
    """Lanza una excepción. Se prohíbe la eliminación para mantener la trazabilidad."""
    raise PermissionError(
        f"No se permite eliminar el envío '{id_envio}'. "
        "Un envío asociado a un pedido confirmado no puede ser borrado para garantizar la trazabilidad."
    )


# --- OPERACIONES DE LOGÍSTICA DE CAMIONES ---

def asignacion_a_dict(asignacion):
    """Convierte un objeto de asignación de camión a un diccionario."""
    return {
        "id_envio_camion_nor": asignacion.id_envio_camion_nor,
        "id_envio": asignacion.id_envio,
        "id_camion": asignacion.id_camion,
        "fecha_carga": asignacion.fecha_carga.isoformat() if asignacion.fecha_carga else None,
    }


def asignar_camion(id_envio, data):
    """Registra un camión para realizar el despacho del envío."""
    envio = Envio.query.get(id_envio)
    if envio is None:
        return None

    asignacion = AsignacionCamiones(
        id_envio_camion_nor=data["id_envio_camion_nor"],
        id_envio=id_envio,
        id_camion=data["id_camion"],
        fecha_carga=data.get("fecha_carga", date.today()),
    )
    db.session.add(asignacion)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"No se pudo asignar el camión: {e.orig}") from e

    return asignacion


def desasignar_camion(id_envio, id_envio_camion_nor):
    """Elimina la asignación de un camión del despacho del envío."""
    asignacion = AsignacionCamiones.query.get(id_envio_camion_nor)
    if asignacion is None or asignacion.id_envio != id_envio:
        return "no_encontrado"

    db.session.delete(asignacion)
    db.session.commit()
    return "eliminado"