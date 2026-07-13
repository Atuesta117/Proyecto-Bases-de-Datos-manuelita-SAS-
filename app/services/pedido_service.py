from app import db
from app.models.pedido import Pedido, DetallePedido, VerificarPedido, DetallePedidoLote
from app.models.producto import Producto
from app.models.lote import Lote
from sqlalchemy.exc import IntegrityError


def obtener_todos_los_pedidos():
    return Pedido.query.all()


def obtener_pedido_por_id(id_pedido):
    return Pedido.query.get(id_pedido)


def crear_pedido(data):
    """
    Crea el pedido (encabezado) + sus líneas. No toca stock todavía;
    eso solo pasa al verificar.

    data esperado:
    {
        "id_pedido": "...",
        "id_cliente": "...",
        "observaciones": "...",
        "items": [{"id_detalle_pedido": "...", "id_producto": "...", "cantidad_solicitada": 5}, ...]
    }
    """
    if not data.get("items"):
        raise ValueError("El pedido debe incluir al menos un producto en 'items'.")

    nuevo_pedido = Pedido(
        id_pedido=data["id_pedido"],
        id_cliente=data["id_cliente"],
        estado="pendiente",
        observaciones=data.get("observaciones"),
    )
    db.session.add(nuevo_pedido)

    for item in data["items"]:
        if item.get("cantidad_solicitada", 0) <= 0:
            raise ValueError("La cantidad solicitada debe ser mayor a cero.")
        db.session.add(
            DetallePedido(
                id_detalle_pedido=item["id_detalle_pedido"],
                id_pedido=data["id_pedido"],
                id_producto=item["id_producto"],
                cantidad_solicitada=item["cantidad_solicitada"],
            )
        )

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"Error de integridad al crear el pedido: {e.orig}")

    return nuevo_pedido


def _lotes_disponibles_fefo(id_producto):
    """
    Devuelve [(lote, unidades_libres), ...] ordenados FEFO (el que vence
    primero sale primero). 'unidades_libres' descuenta lo que ya está
    comprometido con OTROS pedidos que siguen en 'pendiente' o 'verificado'
    (es decir, que ya reservaron ese lote pero aún no se han facturado).
    """
    lotes = (
        Lote.query.filter(Lote.id_producto == id_producto, Lote.cantidad_actual > 0)
        .order_by(Lote.fecha_vencimiento.asc())
        .all()
    )

    disponibles = []
    for lote in lotes:
        comprometido = (
            db.session.query(
                db.func.coalesce(db.func.sum(DetallePedidoLote.cantidad_asignada), 0)
            )
            .join(
                DetallePedido,
                DetallePedidoLote.id_detalle_pedido == DetallePedido.id_detalle_pedido,
            )
            .join(Pedido, DetallePedido.id_pedido == Pedido.id_pedido)
            .filter(
                DetallePedidoLote.id_lote == lote.id_lote,
                Pedido.estado.in_(("pendiente", "verificado")),
            )
            .scalar()
        )
        libre = lote.cantidad_actual - comprometido
        if libre > 0:
            disponibles.append((lote, libre))
    return disponibles


def verificar_pedido(id_pedido, observaciones=None):
    """
    Revisa si hay stock suficiente (por lote, FEFO) para cada producto del
    pedido. Si alcanza para TODOS los productos: reserva las cantidades
    (sube cantidad_reservada, registra qué lotes se usarán) y pasa el
    pedido a 'verificado'. Si no alcanza para algún producto: no reserva
    nada y el pedido pasa a 'rechazado'.
    """
    pedido = Pedido.query.get(id_pedido)
    if not pedido:
        raise ValueError("El pedido no existe.")
    if pedido.estado != "pendiente":
        raise ValueError(
            f"Solo se pueden verificar pedidos en estado 'pendiente' (actual: '{pedido.estado}')."
        )

    plan_asignacion = {}
    es_valido = True
    motivos = []

    for detalle in pedido.detalles:
        faltante = detalle.cantidad_solicitada
        asignaciones = []
        for lote, libre in _lotes_disponibles_fefo(detalle.id_producto):
            if faltante <= 0:
                break
            tomar = min(libre, faltante)
            asignaciones.append((lote, tomar))
            faltante -= tomar

        if faltante > 0:
            es_valido = False
            motivos.append(
                f"Producto {detalle.id_producto}: faltan {faltante} unidades "
                f"de las {detalle.cantidad_solicitada} solicitadas."
            )
        else:
            plan_asignacion[detalle.id_detalle_pedido] = asignaciones

    verificacion = VerificarPedido(
        id_verificacion=f"VER-{id_pedido}",
        id_pedido=id_pedido,
        es_valido=es_valido,
        observaciones=observaciones
        or (
            "; ".join(motivos)
            if motivos
            else "Stock suficiente para todos los productos."
        ),
    )
    db.session.add(verificacion)

    if es_valido:
        pedido.estado = "verificado"
        contador = 0
        for detalle in pedido.detalles:
            for lote, cantidad in plan_asignacion[detalle.id_detalle_pedido]:
                contador += 1
                db.session.add(
                    DetallePedidoLote(
                        id_asignacion=f"ASG-{id_pedido}-{contador}",
                        id_detalle_pedido=detalle.id_detalle_pedido,
                        id_lote=lote.id_lote,
                        cantidad_asignada=cantidad,
                    )
                )
            # Reservamos a nivel de STOCKPRODUCTOS (no descontamos disponible aún)
            producto = Producto.query.get(detalle.id_producto)
            producto.stock.cantidad_reservada += detalle.cantidad_solicitada
    else:
        pedido.estado = "rechazado"

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"Error de integridad al verificar el pedido: {e.orig}")

    return verificacion
