from flask import Blueprint, render_template, request, redirect, url_for, abort
from app.services import (
    factura_service,
    pedido_service,
    cliente_service,
    producto_service,
)
from app.models.factura import Factura
import re

facturas_bp = Blueprint("facturas_views", __name__, url_prefix="/facturas")


def generar_siguiente_id_factura():
    """Busca el último ID FAC-XXXXXX en la base de datos y le suma 1."""
    facturas = Factura.query.filter(Factura.id_factura.like("FAC-%")).all()
    if not facturas:
        return "FAC-000001"

    max_numero = 0
    for f in facturas:
        match = re.match(r"FAC-(\d+)", f.id_factura)
        if match:
            numero = int(match.group(1))
            if numero > max_numero:
                max_numero = numero
    return f"FAC-{max_numero + 1:06d}"


def generar_siguiente_numero_factura():
    """Busca el último número de factura N-FAC-XXXXXX y le suma 1."""
    facturas = Factura.query.filter(Factura.numero_factura.like("FE-%")).all()
    if not facturas:
        return "FE-0000001"

    max_numero = 0
    for f in facturas:
        match = re.match(r"FE-(\d+)", f.numero_factura)
        if match:
            numero = int(match.group(1))
            if numero > max_numero:
                max_numero = numero
    return f"FE-{max_numero + 1:06d}"


def _envio_desde_form(form):
    """Arma el sub-diccionario 'envio' que espera el servicio de facturación."""
    tipo_envio = form.get("tipo_envio")

    envio = {
        "id_envio": form.get("id_envio"),
        "id_sede_origen": form.get("id_sede_origen"),
        "direccion_origen": form.get("direccion_origen"),
        "direccion_destino": form.get("direccion_destino"),
        "fecha_entrega_estimada": form.get("fecha_entrega_estimada") or None,
        "tipo_envio": tipo_envio,
    }

    if tipo_envio == "nacional":
        envio.update(
            {
                "departamento": form.get("departamento"),
                "ciudad": form.get("ciudad"),
                "codigo_postal": form.get("codigo_postal"),
                "transportadora_local": form.get("transportadora_local"),
            }
        )
    elif tipo_envio == "internacional":
        envio.update(
            {
                "pais_destino": form.get("pais_destino"),
                "aduana": form.get("aduana") or None,
                "numero_tracking_internacional": form.get(
                    "numero_tracking_internacional"
                ),
                "costo_aduana": float(form.get("costo_aduana") or 0),
                "divisa": form.get("divisa") or "USD",
            }
        )

    # fecha_entrega_estimada es opcional: si viene vacía la quitamos para que
    # el servicio aplique su valor por defecto (+5 días).
    if not envio["fecha_entrega_estimada"]:
        envio.pop("fecha_entrega_estimada")

    return envio


@facturas_bp.route("/")
def ver_facturas():
    facturas = Factura.query.order_by(Factura.fecha_generacion.desc()).all()
    return render_template("facturas.html", facturas=facturas)


@facturas_bp.route("/<string:id_factura>")
def ver_factura_detalle(id_factura):
    factura = Factura.query.get(id_factura)
    if not factura:
        abort(404)

    cliente = cliente_service.obtener_cliente_por_id(factura.id_cliente)
    productos = {
        p.id_producto: p for p in producto_service.obtener_todos_los_productos()
    }

    return render_template(
        "factura_detalle.html",
        factura=factura,
        cliente=cliente,
        productos=productos,
    )


@facturas_bp.route("/pedido/<string:id_pedido>/nueva", methods=["GET", "POST"])
def generar_factura_view(id_pedido):
    """
    Genera la factura a partir de un pedido. REGLA DEL NEGOCIO: solo se
    puede facturar un pedido que ya existe y está en estado 'verificado'.
    """
    pedido = pedido_service.obtener_pedido_por_id(id_pedido)
    if not pedido:
        abort(404)

    cliente = cliente_service.obtener_cliente_por_id(pedido.id_cliente)
    productos = {
        p.id_producto: p for p in producto_service.obtener_todos_los_productos()
    }

    # Si el pedido no está verificado ni siquiera mostramos el formulario
    if pedido.estado != "verificado":
        return render_template(
            "factura_form.html",
            pedido=pedido,
            cliente=cliente,
            productos=productos,
            error=(
                f"El pedido está en estado '{pedido.estado}'. Solo se puede "
                "facturar un pedido 'verificado'. Verifica el pedido primero."
            ),
        ), 400

    if request.method == "POST":
        # Extraemos los campos desde el formulario (los cuales serán readonly)
        data = {
            "id_factura": request.form.get("id_factura"),
            "numero_factura": request.form.get("numero_factura"),
            "id_empresa": request.form.get("id_empresa"),
            "metodo_pago": request.form.get("metodo_pago") or None,
            "envio": _envio_desde_form(request.form),
        }
        try:
            factura, _envio = factura_service.confirmar_pedido_y_generar_factura(
                id_pedido, data
            )
            return redirect(
                url_for(
                    "facturas_views.ver_factura_detalle", id_factura=factura.id_factura
                )
            )
        except ValueError as e:
            # Si falla, recalculamos los IDs para volver a renderizar con seguridad
            siguiente_id = generar_siguiente_id_factura()
            siguiente_numero = generar_siguiente_numero_factura()
            return render_template(
                "factura_form.html",
                pedido=pedido,
                cliente=cliente,
                productos=productos,
                siguiente_id=siguiente_id,
                siguiente_numero=siguiente_numero,
                error=str(e),
            ), 400

    # En la carga GET, generamos los nuevos valores
    siguiente_id = generar_siguiente_id_factura()
    siguiente_numero = generar_siguiente_numero_factura()
    return render_template(
        "factura_form.html",
        pedido=pedido,
        cliente=cliente,
        productos=productos,
        siguiente_id=siguiente_id,
        siguiente_numero=siguiente_numero,
        error=None,
    )
