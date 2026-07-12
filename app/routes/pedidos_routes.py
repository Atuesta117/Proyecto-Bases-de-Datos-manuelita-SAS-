from flask import Blueprint, request, jsonify
from app.services import pedido_service

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/api/pedidos")


@pedidos_bp.route("/", methods=["GET"])
def listar_pedidos():
    pedidos = pedido_service.obtener_todos_los_pedidos()
    return jsonify([p.to_dict() for p in pedidos]), 200


@pedidos_bp.route("/<string:id_pedido>", methods=["GET"])
def obtener_pedido(id_pedido):
    pedido = pedido_service.obtener_pedido_por_id(id_pedido)
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404
    return jsonify(pedido.to_dict()), 200


@pedidos_bp.route("/", methods=["POST"])
def registrar_pedido():
    data = request.get_json()
    campos = ["id_pedido", "id_cliente", "items"]
    if any(c not in data for c in campos):
        return jsonify(
            {"error": "Faltan campos obligatorios para generar el pedido"}
        ), 400

    try:
        nuevo = pedido_service.crear_pedido(data)
        return jsonify(nuevo.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@pedidos_bp.route("/<string:id_pedido>/verificar", methods=["POST"])
def verificar_pedido(id_pedido):
    """El sistema revisa stock disponible (por lote, FEFO) para cada producto del pedido"""
    data = request.get_json() or {}
    try:
        verificacion = pedido_service.verificar_pedido(
            id_pedido, data.get("observaciones")
        )
        return jsonify(
            {
                "mensaje": "Verificación completada"
                + (" y stock reservado." if verificacion.es_valido else "."),
                "verificacion": verificacion.to_dict(),
            }
        ), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# No se exponen PUT/DELETE: un pedido solo avanza a través de /verificar
# y de la confirmación de factura, cumpliendo la regla de inmutabilidad.
