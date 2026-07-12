from app import db
from app.models.orden_proveedor import OrdenPedidoProveedor, DetalleOrdenPedidoProveedor
from app.models.lote import Lote
from app.services.producto_service import sumar_stock_disponible
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError


def obtener_todas_las_ordenes():
    return OrdenPedidoProveedor.query.all()


def crear_orden_pendiente(data):
    """
    Crea la orden (encabezado) + sus líneas de detalle (uno o varios productos).
    No altera stock aún: eso solo pasa al 'recibir'.

    data esperado:
    {
        "id_orden": "...",
        "id_sede": "...",
        "id_proveedor": "...",
        "lugar_entrega": "...",
        "items": [
            {"id_detalle_orden": "...", "id_producto": "...", "cantidad": 10, "costo_unitario": 5000},
            ...
        ]
    }
    """
    if not data.get("items"):
        raise ValueError("La orden debe incluir al menos un producto en 'items'.")

    nueva_orden = OrdenPedidoProveedor(
        id_orden=data["id_orden"],
        id_sede=data["id_sede"],
        id_proveedor=data["id_proveedor"],
        lugar_entrega=data["lugar_entrega"],
        estado="pendiente",
    )
    db.session.add(nueva_orden)

    for item in data["items"]:
        if item.get("cantidad", 0) <= 0:
            raise ValueError("La cantidad pedida debe ser mayor a cero.")
        detalle = DetalleOrdenPedidoProveedor(
            id_detalle_orden=item["id_detalle_orden"],
            id_orden=data["id_orden"],
            id_producto=item["id_producto"],
            cantidad=item["cantidad"],
            costo_unitario=item["costo_unitario"],
        )
        db.session.add(detalle)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"Error de integridad al crear la orden: {e.orig}")

    return nueva_orden


def recibir_orden_proveedor(id_orden, dias_para_vencer=365):
    """
    Cambia el estado a 'recibido', genera un lote POR CADA línea de detalle
    y actualiza el stock físico de cada producto involucrado. Todo en una
    sola transacción: si algo falla, no queda nada a medias.
    """
    orden = OrdenPedidoProveedor.query.get(id_orden)
    if not orden:
        raise ValueError("La orden especificada no existe.")

    if orden.estado not in ("pendiente", "en_transito"):
        raise ValueError(
            f"No se puede recibir una orden en estado '{orden.estado}'. "
            "Solo se aceptan órdenes en 'pendiente' o 'en_transito'."
        )

    if not orden.detalles:
        raise ValueError("La orden no tiene productos asociados (sin detalle).")

    orden.estado = "recibido"

    fecha_ingreso = date.today()
    fecha_vence = fecha_ingreso + timedelta(days=dias_para_vencer)

    for detalle in orden.detalles:
        nuevo_lote = Lote(
            id_lote=f"LOT-{detalle.id_detalle_orden}",
            id_producto=detalle.id_producto,
            id_proveedor=orden.id_proveedor,
            id_sede=orden.id_sede,
            id_detalle_orden=detalle.id_detalle_orden,
            fecha_ingreso=fecha_ingreso,
            fecha_vencimiento=fecha_vence,
            cantidad_inicial=detalle.cantidad,
            cantidad_actual=detalle.cantidad,
        )
        db.session.add(nuevo_lote)

        exito_stock = sumar_stock_disponible(detalle.id_producto, detalle.cantidad)
        if not exito_stock:
            db.session.rollback()
            raise ValueError(
                f"No se pudo actualizar el stock del producto {detalle.id_producto}: "
                "no existe registro en STOCKPRODUCTOS."
            )

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"Error procesando la recepción en DB: {e.orig}")

    return orden
