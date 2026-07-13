from flask import Blueprint, request, jsonify
from app.services import proveedor_service

proveedores_api_bp = Blueprint(
    "proveedores_api", __name__, url_prefix="/api/proveedores"
)


@proveedores_api_bp.route("/", methods=["GET"])
def listar_proveedores():
    proveedores = proveedor_service.obtener_todos_los_proveedores()
    return jsonify([p.to_dict() for p in proveedores]), 200


@proveedores_api_bp.route("/<string:id_proveedor>", methods=["GET"])
def obtener_proveedor(id_proveedor):
    proveedor = proveedor_service.obtener_proveedor_por_id(id_proveedor)
    if proveedor is None:
        return jsonify({"error": "Proveedor no encontrado"}), 404
    return jsonify(proveedor.to_dict()), 200


@proveedores_api_bp.route("/", methods=["POST"])
def crear_proveedor():
    data = request.get_json()

    campos_obligatorios = [
        "id_proveedor",
        "nombre_razon_social",
        "tipo_documento",
        "numero_identificacion",
        "email",
        "rut",
    ]
    faltantes = [c for c in campos_obligatorios if c not in data]
    if faltantes:
        return jsonify({"error": f"Faltan campos obligatorios: {faltantes}"}), 400

    try:
        nuevo = proveedor_service.crear_proveedor(data)
    except (ValueError, Exception) as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(nuevo.to_dict()), 201


@proveedores_api_bp.route("/<string:id_proveedor>", methods=["PUT"])
def actualizar_proveedor(id_proveedor):
    data = request.get_json()

    try:
        proveedor = proveedor_service.actualizar_proveedor(id_proveedor, data)
    except (ValueError, Exception) as e:
        return jsonify({"error": str(e)}), 400

    if proveedor is None:
        return jsonify({"error": "Proveedor no encontrado"}), 404
    return jsonify(proveedor.to_dict()), 200


@proveedores_api_bp.route("/<string:id_proveedor>", methods=["DELETE"])
def eliminar_proveedor(id_proveedor):
    resultado = proveedor_service.eliminar_proveedor(id_proveedor)

    if resultado == "no_encontrado":
        return jsonify({"error": "Proveedor no encontrado"}), 404
    if resultado == "tiene_ordenes":
        return jsonify(
            {
                "error": "No se puede eliminar: el proveedor tiene órdenes de pedido asociadas"
            }
        ), 409
    if resultado == "tiene_productos":
        return jsonify(
            {
                "error": "No se puede eliminar: el proveedor tiene productos/insumos asociados"
            }
        ), 409
    if resultado == "tiene_registros_asociados":
        return jsonify(
            {
                "error": "No se puede eliminar: el proveedor tiene registros contables o de inventario asociados"
            }
        ), 409

    return jsonify({"mensaje": "Proveedor eliminado con éxito"}), 200
