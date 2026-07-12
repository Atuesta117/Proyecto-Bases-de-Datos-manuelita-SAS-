from flask import Blueprint, request, jsonify
from app.services import cliente_service

clientes_bp = Blueprint("clientes", __name__, url_prefix="/api/clientes")


@clientes_bp.route("/", methods=["GET"])
def listar_clientes():
    clientes = cliente_service.obtener_todos_los_clientes()
    return jsonify([c.to_dict() for c in clientes]), 200


@clientes_bp.route("/<string:id_cliente>", methods=["GET"])
def obtener_cliente(id_cliente):
    cliente = cliente_service.obtener_cliente_por_id(id_cliente)
    if cliente is None:
        return jsonify({"error": "Cliente no encontrado"}), 404
    return jsonify(cliente.to_dict()), 200


@clientes_bp.route("/", methods=["POST"])
def crear_cliente():
    data = request.get_json()

    campos_obligatorios = [
        "id_cliente",
        "tipo_documento",
        "numero_identificacion",
        "nombre_razon_social",
        "email",
        "ciudad",
    ]
    faltantes = [c for c in campos_obligatorios if c not in data]
    if faltantes:
        return jsonify({"error": f"Faltan campos obligatorios: {faltantes}"}), 400

    try:
        nuevo = cliente_service.crear_cliente(data)
    except (ValueError, Exception) as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(nuevo.to_dict()), 201


@clientes_bp.route("/<string:id_cliente>", methods=["PUT"])
def actualizar_cliente(id_cliente):
    data = request.get_json()

    try:
        cliente = cliente_service.actualizar_cliente(id_cliente, data)
    except (ValueError, Exception) as e:
        return jsonify({"error": str(e)}), 400

    if cliente is None:
        return jsonify({"error": "Cliente no encontrado"}), 404
    return jsonify(cliente.to_dict()), 200


@clientes_bp.route("/<string:id_cliente>", methods=["DELETE"])
def eliminar_cliente(id_cliente):
    resultado = cliente_service.eliminar_cliente(id_cliente)

    if resultado == "no_encontrado":
        return jsonify({"error": "Cliente no encontrado"}), 404
    if resultado == "tiene_facturas":
        return jsonify(
            {"error": "No se puede eliminar: el cliente tiene facturas asociadas"}
        ), 409
    if resultado == "tiene_pedidos":
        return jsonify(
            {"error": "No se puede eliminar: el cliente tiene pedidos asociados"}
        ), 409
    if resultado == "tiene_registros_asociados":
        return jsonify(
            {"error": "No se puede eliminar: el cliente tiene registros asociados"}
        ), 409

    return jsonify({"mensaje": "Cliente eliminado"}), 200
