from flask import Blueprint, render_template, abort
from app.services import orden_proveedor_service, proveedor_service, producto_service
from app.models.logistica import (
    Sedes,
)  # Importamos el modelo directamente desde donde está definido
from app.models.orden_proveedor import OrdenPedidoProveedor
import re

ordenes_vistas_bp = Blueprint("ordenes_vistas", __name__, url_prefix="/ordenes")


def generar_siguiente_id_orden():
    """
    Busca el último ID de pedido con formato PED-XXXXXX en la base de datos,
    extrae el número, le suma 1 y formatea el nuevo ID (ej: PED-002002).
    """
    # Buscamos todos los IDs que empiecen con "PED-"
    pedidos = OrdenPedidoProveedor.query.filter(
        OrdenPedidoProveedor.id_orden.like("OPP-%")
    ).all()

    if not pedidos:
        return "OPP-000001"

    max_numero = 0
    for p in pedidos:
        # Extraemos solo la parte numérica usando una expresión regular
        match = re.match(r"OPP-(\d+)", p.id_orden)
        if match:
            numero = int(match.group(1))
            if numero > max_numero:
                max_numero = numero

    siguiente_numero = max_numero + 1
    # Formatea con ceros a la izquierda para garantizar un ancho de 6 dígitos
    return f"OPP-{siguiente_numero:06d}"


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


@ordenes_vistas_bp.route(
    "/nueva", methods=["GET", "POST"]
)  # Agregamos POST si procesas el form aquí
def crear_orden_view():
    proveedores = proveedor_service.obtener_todos_los_proveedores()
    productos = producto_service.obtener_todos_los_productos()
    sedes = Sedes.query.all()

    siguiente_id = generar_siguiente_id_orden()
    return render_template(
        "orden_form.html",
        proveedores=proveedores,
        productos=productos,
        sedes=sedes,
        siguiente_id=siguiente_id,  # <-- Enviamos el ID aquí
    )
