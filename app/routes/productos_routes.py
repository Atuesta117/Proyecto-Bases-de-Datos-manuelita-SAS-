from flask import Blueprint, request, jsonify
from app.services import producto_service

productos_api_bp = Blueprint("productos", __name__, url_prefix="/api/productos")


@productos_api_bp.route("/", methods=["GET"])
def listar_productos():
    productos = producto_service.obtener_todos_los_productos()
    # Retorna la info con el stock y el cálculo de días de inventario directo al vuelo
    return jsonify([p.to_dict_completo() for p in productos]), 200


@productos_api_bp.route("/<string:id_producto>", methods=["GET"])
def obtener_producto(id_producto):
    producto = producto_service.obtener_producto_por_id(id_producto)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(producto.to_dict_completo()), 200


@productos_api_bp.route("/<string:id_producto>/lotes", methods=["GET"])
def obtener_lotes_de_producto(id_producto):
    """Ruta solicitada para ver los lotes de cada producto y sus unidades actuales"""
    lotes = producto_service.obtener_lotes_por_producto(id_producto)
    return jsonify(lotes), 200


@productos_api_bp.route("/", methods=["POST"])
def crear_producto():
    data = request.get_json()
    campos_obligatorios = [
        "id_producto",
        "nombre",
        "id_proveedor",
        "id_tipo_iva",
        "precio",
        "categoria",
        "peso",
    ]

    faltantes = [c for c in campos_obligatorios if c not in data]
    if faltantes:
        return jsonify({"error": f"Faltan campos obligatorios: {faltantes}"}), 400

    try:
        nuevo = producto_service.crear_producto(data)
        return jsonify(nuevo.to_dict_completo()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@productos_api_bp.route("/<string:id_producto>", methods=["PUT"])
def actualizar_producto(id_producto):
    data = request.get_json()
    try:
        producto = producto_service.actualizar_producto(id_producto, data)
        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404
        return jsonify(producto.to_dict_completo()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@productos_api_bp.route("/<string:id_producto>", methods=["DELETE"])
def eliminar_producto(id_producto):
    exito = producto_service.eliminar_logico_producto(id_producto)
    if not exito:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify({"mensaje": "Producto inactivado lógicamente con éxito"}), 200
