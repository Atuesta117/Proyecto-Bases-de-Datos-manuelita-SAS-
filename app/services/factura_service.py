from app import db
from app.models.pedido import Pedido, DetallePedidoLote
from app.models.factura import Factura, DetalleFactura, PedidoConfirmado
from app.models.producto import Producto
from app.models.lote import Lote
from app.models.logistica import (
    Camion,
    Conductor,
    CamionConductor,
    Envio,
    EnvioNacional,
    EnvioInternacional,
    AsignacionCamiones,
)
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError


def _calcular_detalle_factura(id_detalle, id_producto, cantidad, id_factura):
    """Calcula subtotal/IVA/total de una línea usando el % de IVA real del producto."""
    producto = Producto.query.get(id_producto)
    if not producto:
        raise ValueError(f"El producto {id_producto} no existe.")

    porcentaje = float(producto.tipo_iva.porcentaje) if producto.tipo_iva else 0.0
    precio_unitario = producto.precio

    subtotal_item = precio_unitario * cantidad
    valor_iva = round(subtotal_item * porcentaje / 100)
    total_item = subtotal_item + valor_iva

    return DetalleFactura(
        id_detalle=id_detalle,
        id_factura=id_factura,
        id_producto=id_producto,
        cantidad=cantidad,
        precio_unitario=precio_unitario,
        porcentaje_iva=porcentaje,
        valor_iva=valor_iva,
        subtotal_item=subtotal_item,
        total_item=total_item,
    )


def _consumir_stock_del_pedido(pedido):
    """
    Ahora sí descuenta físicamente lo reservado: baja cantidad_actual de
    cada lote asignado y cantidad_disponible/cantidad_reservada del stock
    del producto. Se llama solo al confirmar (facturar), nunca antes.
    """
    for detalle in pedido.detalles:
        producto = Producto.query.get(detalle.id_producto)

        for asignacion in detalle.asignaciones_lote:
            lote = Lote.query.get(asignacion.id_lote)
            lote.cantidad_actual -= asignacion.cantidad_asignada

        producto.stock.cantidad_disponible -= detalle.cantidad_solicitada
        producto.stock.cantidad_reservada -= detalle.cantidad_solicitada


def _asignar_camion_y_conductor_disponibles(id_sede_origen, id_envio):
    """
    Busca UN camión y UN conductor disponibles en la sede de origen del
    envío. Si no hay ninguno disponible, lanza ValueError (no tiene
    sentido asignar "cualquier" camión, como bien lo señalaste).
    """
    camion = Camion.query.filter_by(id_sede=id_sede_origen, estado="disponible").first()
    if not camion:
        raise ValueError(
            f"No hay camiones disponibles en la sede '{id_sede_origen}' para despachar el envío."
        )

    conductor = Conductor.query.filter_by(
        id_sede=id_sede_origen, disponible=True
    ).first()
    if not conductor:
        raise ValueError(
            f"No hay conductores disponibles en la sede '{id_sede_origen}' para despachar el envío."
        )

    # Registramos quién conduce este camión desde hoy (si no hay una
    # asignación activa vigente para este camión, abrimos una nueva)
    asignacion_activa = CamionConductor.query.filter_by(
        id_camion=camion.id_camion, fecha_fin=None
    ).first()
    if not asignacion_activa:
        db.session.add(
            CamionConductor(
                id_camion_conductor=f"CC-{camion.id_camion}-{conductor.id_conductor}-{date.today().isoformat()}",
                id_camion=camion.id_camion,
                id_conductor=conductor.id_conductor,
                fecha_inicio=date.today(),
            )
        )

    db.session.add(
        AsignacionCamiones(
            id_envio_camion_nor=f"ASGCAM-{id_envio}",
            id_envio=id_envio,
            id_camion=camion.id_camion,
        )
    )

    # Marcamos ambos como ocupados hasta que el envío se entregue
    camion.estado = "en_ruta"
    conductor.disponible = False

    return camion, conductor


def confirmar_pedido_y_generar_factura(id_pedido, data):
    """
    Flujo completo: pedido verificado -> factura (con IVA calculado por
    producto) -> descuento físico de stock -> envío (nacional o
    internacional) con camión/conductor asignados según disponibilidad
    real en la sede de despacho.

    data esperado:
    {
        "id_factura": "...", "numero_factura": "...", "id_empresa": "...",
        "metodo_pago": "efectivo|tarjeta|transferencia|contraentrega",

        "envio": {
            "id_envio": "...",
            "id_sede_origen": "...",
            "direccion_origen": "...",
            "direccion_destino": "...",
            "fecha_entrega_estimada": "YYYY-MM-DD",   # opcional, default +5 días
            "tipo_envio": "nacional" | "internacional",

            # si tipo_envio == "nacional":
            "departamento": "...", "ciudad": "...", "codigo_postal": "...",
            "transportadora_local": "...",

            # si tipo_envio == "internacional":
            "pais_destino": "...", "aduana": "...",
            "numero_tracking_internacional": "...",
            "costo_aduana": 0.0, "divisa": "USD"
        }
    }
    """
    pedido = Pedido.query.get(id_pedido)
    if not pedido:
        raise ValueError("El pedido no existe.")
    if pedido.estado != "verificado":
        raise ValueError(
            f"Solo se pueden facturar pedidos en estado 'verificado' (actual: '{pedido.estado}')."
        )
    if not pedido.verificacion or not pedido.verificacion.es_valido:
        raise ValueError("El pedido no tiene una verificación válida asociada.")

    id_factura = data["id_factura"]

    # --- 1. Calculamos cada línea de factura con el IVA real del producto ---
    detalles_factura = []
    subtotal_total = 0
    iva_total = 0
    total_total = 0
    contador = 0
    for detalle_pedido in pedido.detalles:
        contador += 1
        detalle_factura = _calcular_detalle_factura(
            id_detalle=f"DF-{id_factura}-{contador}",
            id_producto=detalle_pedido.id_producto,
            cantidad=detalle_pedido.cantidad_solicitada,
            id_factura=id_factura,
        )
        detalles_factura.append(detalle_factura)
        subtotal_total += detalle_factura.subtotal_item
        iva_total += detalle_factura.valor_iva
        total_total += detalle_factura.total_item

    factura = Factura(
        id_factura=id_factura,
        id_empresa=data["id_empresa"],
        id_cliente=pedido.id_cliente,
        numero_factura=data["numero_factura"],
        metodo_pago=data.get("metodo_pago"),
        estado="confirmado",
        subtotal=subtotal_total,
        valor_iva=iva_total,
        total_pagar=total_total,
    )
    db.session.add(factura)
    for d in detalles_factura:
        db.session.add(d)

    # --- 2. Descontamos físicamente el inventario reservado ---
    _consumir_stock_del_pedido(pedido)

    # --- 3. Cerramos el ciclo del pedido ---
    pedido.estado = "confirmado"
    pedido_confirmado = PedidoConfirmado(
        id_confirmacion=f"CONF-{id_pedido}",
        id_verificacion=pedido.verificacion.id_verificacion,
        id_factura=id_factura,
        es_valido=True,
    )
    db.session.add(pedido_confirmado)

    # --- 4. Generamos el envío + asignamos camión/conductor de la sede ---
    envio_data = data["envio"]
    id_sede_origen = envio_data["id_sede_origen"]
    fecha_entrega_estimada = envio_data.get(
        "fecha_entrega_estimada", (date.today() + timedelta(days=5)).isoformat()
    )

    nuevo_envio = Envio(
        id_envio=envio_data["id_envio"],
        id_pedido_confirmado=pedido_confirmado.id_confirmacion,
        id_sede_origen=id_sede_origen,
        direccion_origen=envio_data["direccion_origen"],
        direccion_destino=envio_data["direccion_destino"],
        fecha_entrega_estimada=fecha_entrega_estimada,
        estado_envio="preparando",
        tipo_envio=envio_data["tipo_envio"],
    )
    db.session.add(nuevo_envio)

    if envio_data["tipo_envio"] == "nacional":
        db.session.add(
            EnvioNacional(
                id_envio=envio_data["id_envio"],
                departamento=envio_data["departamento"],
                ciudad=envio_data["ciudad"],
                codigo_postal=envio_data["codigo_postal"],
                transportadora_local=envio_data["transportadora_local"],
            )
        )
    elif envio_data["tipo_envio"] == "internacional":
        db.session.add(
            EnvioInternacional(
                id_envio=envio_data["id_envio"],
                pais_destino=envio_data["pais_destino"],
                aduana=envio_data.get("aduana"),
                numero_tracking_internacional=envio_data[
                    "numero_tracking_internacional"
                ],
                costo_aduana=envio_data["costo_aduana"],
                divisa=envio_data["divisa"],
            )
        )
    else:
        raise ValueError("tipo_envio debe ser 'nacional' o 'internacional'.")

    # --- 5. Asignamos camión/conductor DISPONIBLES en esa sede (no "cualquiera") ---
    _asignar_camion_y_conductor_disponibles(id_sede_origen, envio_data["id_envio"])

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"Error de integridad al generar la factura/envío: {e.orig}")

    return factura, nuevo_envio
