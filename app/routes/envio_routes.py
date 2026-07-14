from flask import Blueprint, request, jsonify
from app.services import envio_service

envios_api_bp = Blueprint("envios_api", __name__, url_prefix="/api/envios")


@envios_api_bp.route("/", methods=["GET"])
def listar_envios():
    envios = envio_service.obtener_todos_los_envios()
    return jsonify([e.to_dict() for e in envios]), 200


@envios_api_bp.route("/<string:id_envio>", methods=["GET"])
def obtener_envio(id_envio):
    detalle = envio_service.obtener_detalle_envio(id_envio)
    if detalle is None:
        return jsonify({"error": "Envío no encontrado"}), 404
    return jsonify(detalle), 200
