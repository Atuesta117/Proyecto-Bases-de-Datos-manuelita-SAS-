from flask import Blueprint, request, jsonify
from app.services import orden_proveedor_service

ordenes_api_bp = Blueprint("ordenes", __name__, url_prefix="/api/ordenes")


@ordenes_api_bp.route("/", methods=["GET"])
def listar_ordenes():
    ordenes = orden_proveedor_service.obtener_todas_las_ordenes()
    return jsonify([o.to_dict() for o in ordenes]), 200


@ordenes_api_bp.route("/", methods=["POST"])
def registrar_orden():
    data = request.get_json()
    campos = ["id_orden", "id_sede", "id_proveedor", "lugar_entrega", "items"]
    if any(c not in data for c in campos):
        return jsonify(
            {"error": "Faltan campos obligatorios para generar la orden"}
        ), 400

    try:
        nueva = orden_proveedor_service.crear_orden_pendiente(data)
        return jsonify(nueva.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@ordenes_api_bp.route("/<string:id_orden>/recibir", methods=["POST"])
def recibir_pedido(id_orden):
    """El frontend le pega aquí cuando el camión llega y dan clic en 'Recibir'"""
    data = request.get_json() or {}
    dias_vence = data.get("dias_para_vencer", 365)

    try:
        orden_procesada = orden_proveedor_service.recibir_orden_proveedor(
            id_orden, dias_vence
        )
        return jsonify(
            {
                "mensaje": "Pedido recibido de forma exitosa. Lotes generados e inventario actualizado.",
                "orden": orden_procesada.to_dict(),
            }
        ), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# No se exponen PUT/DELETE para /ordenes: una vez creada, una orden y su
# estado solo avanzan a través de /recibir, cumpliendo la regla de
# inmutabilidad del rastro transaccional.
