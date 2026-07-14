from flask import Blueprint, render_template, abort, jsonify, request
from app.services import envio_service
from app import db
from sqlalchemy import text

envios_bp = Blueprint("envios", __name__, url_prefix="/envios")


def obtener_camiones_raw():
    """Consulta la tabla CAMION para el selector de asignación."""
    query = text("SELECT id_camion, placa, modelo FROM CAMION")
    resultado = db.session.execute(query)
    return [
        {"id_camion": row.id_camion, "placa": row.placa, "modelo": row.modelo}
        for row in resultado
    ]


@envios_bp.route("/")
def ver_envios():
    """Muestra el panel general de envíos activos sin opciones de creación."""
    envios = envio_service.obtener_todos_los_envios()
    return render_template("envios.html", envios=envios)


@envios_bp.route("/<string:id_envio>")
def ver_envio_detalle(id_envio):
    """Muestra la ficha técnica detallada del envío y la asignación de transporte."""
    envio_detallado = envio_service.obtener_detalle_envio(id_envio)
    if not envio_detallado:
        abort(404)

    from app.models.logistica import AsignacionCamiones
    asignaciones_db = AsignacionCamiones.query.filter_by(id_envio=id_envio).all()
    asignaciones = [envio_service.asignacion_a_dict(a) for a in asignaciones_db]

    camiones = obtener_camiones_raw()

    return render_template(
        "envio_detalle.html",
        envio=envio_detallado,
        asignaciones=asignaciones,
        camiones=camiones
    )


# --- SEGURIDAD: RUTAS DE ESCRITURA BLOQUEADAS DESDE EL SERVIDOR ---

@envios_bp.route("/crear", methods=["GET", "POST"])
def crear_envio():
    mensaje = "Acción denegada. Los envíos se crean únicamente de manera automática por flujo de pedidos."
    return jsonify({"error": mensaje}), 403


@envios_bp.route("/editar/<string:id_envio>", methods=["GET", "POST"])
def editar_envio(id_envio):
    mensaje = f"Acción denegada. El envío '{id_envio}' es inmutable."
    return jsonify({"error": mensaje}), 403


@envios_bp.route("/eliminar/<string:id_envio>", methods=["POST", "DELETE"])
def eliminar_envio(id_envio):
    mensaje = f"Acción denegada. No se permite eliminar el envío '{id_envio}' para preservar la auditoría."
    return jsonify({"error": mensaje}), 403


# --- OPERACIONES LOGÍSTICAS DE TRANSPORTE PERMITIDAS ---

@envios_bp.route("/<string:id_envio>/asignar-camion", methods=["POST"])
def asignar_camion(id_envio):
    """Asocia un camión al envío activo."""
    data = request.get_json() or request.form
    try:
        asignacion = envio_service.asignar_camion(id_envio, data)
        if not asignacion:
            return jsonify({"error": "Envío no encontrado"}), 404
        return jsonify({
            "success": True,
            "mensaje": "Camión asignado exitosamente",
            "asignacion": envio_service.asignacion_a_dict(asignacion)
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@envios_bp.route("/<string:id_envio>/desasignar-camion/<string:id_envio_camion_nor>", methods=["POST", "DELETE"])
def desasignar_camion(id_envio, id_envio_camion_nor):
    """Desvincula un camión del envío."""
    resultado = envio_service.desasignar_camion(id_envio, id_envio_camion_nor)
    if resultado == "no_encontrado":
        return jsonify({"error": "La asignación no pertenece a este envío"}), 404
    return jsonify({"success": True, "mensaje": "Asignación removida correctamente"}), 200