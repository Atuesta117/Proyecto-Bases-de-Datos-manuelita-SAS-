from flask import Blueprint, render_template, abort
from app.services import orden_proveedor_service, proveedor_service, producto_service
from app.models.logistica import (
    Sedes,
)  # Importamos el modelo directamente desde donde está definido

ordenes_vistas_bp = Blueprint("ordenes_vistas", __name__, url_prefix="/ordenes")


@ordenes_vistas_bp.route("/")
def ver_ordenes():
    # Obtiene todas las órdenes para el listado principal
    ordenes = orden_proveedor_service.obtener_todas_las_ordenes()
    return render_template("ordenes.html", ordenes=ordenes)


@ordenes_vistas_bp.route("/<string:id_orden>")
def ver_orden_detalle(id_orden):
    orden = orden_proveedor_service.OrdenPedidoProveedor.query.get(id_orden)
    if not orden:
        abort(404)
    return render_template("orden_detalle.html", orden=orden)


@ordenes_vistas_bp.route("/nueva", methods=["GET"])
def crear_orden_view():
    # Cargamos los datos para los selectores utilizando los servicios existentes
    proveedores = proveedor_service.obtener_todos_los_proveedores()
    productos = producto_service.obtener_todos_los_productos()

    # Consultamos las sedes directamente desde el modelo de base de datos
    sedes = Sedes.query.all()

    return render_template(
        "orden_form.html", proveedores=proveedores, productos=productos, sedes=sedes
    )
