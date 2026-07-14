from flask import Blueprint, request, jsonify
from app.services import conductor_service

conductores_api_bp = Blueprint(
    "conductores_api", __name__, url_prefix="/api/conductores"
)


@conductores_api_bp.route("/", methods=["GET"])
def listar_conductores():
    conductores = conductor_service.obtener_todos_los_conductores()
    return jsonify([c.to_dict() for c in conductores]), 200


@conductores_api_bp.route("/<string:id_conductor>", methods=["GET"])
def obtener_conductor(id_conductor):
    conductor = conductor_service.obtener_conductor_por_id(id_conductor)
    if conductor is None:
        return jsonify({"error": "Conductor no encontrado"}), 404
    return jsonify(conductor.to_dict()), 200


@conductores_api_bp.route("/", methods=["POST"])
def crear_conductor():
    data = request.get_json()

    campos_obligatorios = [
        "id_conductor",
        "nombre",
        "apellido",
        "cedula",
        "telefono",
        "licencia",
        "fecha_vencimiento_licencia",
    ]
    faltantes = [c for c in campos_obligatorios if c not in data]
    if faltantes:
        return jsonify({"error": f"Faltan campos obligatorios: {faltantes}"}), 400

    try:
        nuevo = conductor_service.crear_conductor(data)
    except (ValueError, Exception) as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(nuevo.to_dict()), 201


@conductores_api_bp.route("/<string:id_conductor>", methods=["PUT"])
def actualizar_conductor(id_conductor):
    data = request.get_json()

    try:
        conductor = conductor_service.actualizar_conductor(id_conductor, data)
    except (ValueError, Exception) as e:
        return jsonify({"error": str(e)}), 400

    if conductor is None:
        return jsonify({"error": "Conductor no encontrado"}), 404
    return jsonify(conductor.to_dict()), 200


@conductores_api_bp.route("/<string:id_conductor>", methods=["DELETE"])
def eliminar_conductor(id_conductor):
    resultado = conductor_service.eliminar_conductor(id_conductor)

    if resultado == "no_encontrado":
        return jsonify({"error": "Conductor no encontrado"}), 404
    if resultado == "tiene_asignaciones_camion":
        return jsonify(
            {
                "error": "No se puede eliminar: el conductor tiene historial de camiones asociado"
            }
        ), 409
    if resultado == "tiene_registros_asociados":
        return jsonify(
            {"error": "No se puede eliminar: el conductor tiene registros asociados"}
        ), 409

    return jsonify({"mensaje": "Conductor eliminado"}), 200
