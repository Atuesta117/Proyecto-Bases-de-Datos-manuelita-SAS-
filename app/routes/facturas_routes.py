from flask import Blueprint, request, jsonify
from app.services import factura_service
from app.models.factura import Factura

facturas_bp = Blueprint("facturas", __name__, url_prefix="/api/facturas")


@facturas_bp.route("/", methods=["GET"])
def listar_facturas():
    facturas = Factura.query.all()
    return jsonify([f.to_dict() for f in facturas]), 200


@facturas_bp.route("/<string:id_factura>", methods=["GET"])
def obtener_factura(id_factura):
    factura = Factura.query.get(id_factura)
    if not factura:
        return jsonify({"error": "Factura no encontrada"}), 404
    return jsonify(factura.to_dict()), 200


@facturas_bp.route("/pedidos/<string:id_pedido>/confirmar", methods=["POST"])
def confirmar_pedido(id_pedido):
    """
    Endpoint clave: toma un pedido en estado 'verificado', genera su
    factura (con IVA calculado por producto), descuenta el inventario
    físico y crea el envío asignando camión/conductor disponibles.
    """
    data = request.get_json()
    campos = ["id_factura", "numero_factura", "id_empresa", "envio"]
    if any(c not in data for c in campos):
        return jsonify(
            {"error": "Faltan campos obligatorios para generar la factura"}
        ), 400

    try:
        factura, envio = factura_service.confirmar_pedido_y_generar_factura(
            id_pedido, data
        )
        return jsonify(
            {
                "mensaje": "Factura generada, inventario descontado y envío creado con éxito.",
                "factura": factura.to_dict(),
                "envio": envio.to_dict(),
            }
        ), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# No se exponen PUT/DELETE para /facturas: una vez generada, la factura
# es inmutable (normativa de facturación electrónica en Colombia).
