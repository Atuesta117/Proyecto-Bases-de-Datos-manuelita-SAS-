from flask import Blueprint, request, jsonify
from app.services import camion_service

camiones_api_bp = Blueprint("camiones_api", __name__, url_prefix="/api/camiones")


@camiones_api_bp.route("/", methods=["GET"])
def listar_camiones():
    camiones = camion_service.obtener_todos_los_camiones()
    return jsonify([c.to_dict() for c in camiones]), 200


@camiones_api_bp.route("/<string:id_camion>", methods=["GET"])
def obtener_camion(id_camion):
    camion = camion_service.obtener_camion_por_id(id_camion)
    if camion is None:
        return jsonify({"error": "Camión no encontrado"}), 404
    return jsonify(camion.to_dict()), 200


@camiones_api_bp.route("/", methods=["POST"])
def crear_camion():
    data = request.get_json()

    campos_obligatorios = [
        "id_camion",
        "placa",
        "marca",
        "modelo",
        "capacidad_kg",
    ]
    faltantes = [c for c in campos_obligatorios if c not in data]
    if faltantes:
        return jsonify({"error": f"Faltan campos obligatorios: {faltantes}"}), 400

    try:
        nuevo = camion_service.crear_camion(data)
    except (ValueError, Exception) as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(nuevo.to_dict()), 201


@camiones_api_bp.route("/<string:id_camion>", methods=["PUT"])
def actualizar_camion(id_camion):
    data = request.get_json()

    try:
        camion = camion_service.actualizar_camion(id_camion, data)
    except (ValueError, Exception) as e:
        return jsonify({"error": str(e)}), 400

    if camion is None:
        return jsonify({"error": "Camión no encontrado"}), 404
    return jsonify(camion.to_dict()), 200


@camiones_api_bp.route("/<string:id_camion>", methods=["DELETE"])
def eliminar_camion(id_camion):
    resultado = camion_service.eliminar_camion(id_camion)

    if resultado == "no_encontrado":
        return jsonify({"error": "Camión no encontrado"}), 404
    if resultado == "tiene_asignaciones":
        return jsonify(
            {"error": "No se puede eliminar: el camión tiene asignaciones a envíos"}
        ), 409
    if resultado == "tiene_historial_conductores":
        return jsonify(
            {
                "error": "No se puede eliminar: el camión tiene historial de conductores asociado"
            }
        ), 409
    if resultado == "tiene_registros_asociados":
        return jsonify(
            {"error": "No se puede eliminar: el camión tiene registros asociados"}
        ), 409

    return jsonify({"mensaje": "Camión eliminado"}), 200
