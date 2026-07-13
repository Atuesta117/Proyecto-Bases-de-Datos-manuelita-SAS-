from flask import Blueprint, render_template, request, redirect, url_for, abort
from app.services import pedido_service, cliente_service, producto_service

pedidos_bp = Blueprint("pedidos_views", __name__, url_prefix="/pedidos")


def _items_desde_form(form, id_pedido):
    """
    Reconstruye la lista de items del pedido a partir del formulario.
    El formulario envía arrays paralelos: item_producto[] y item_cantidad[].
    Genera el id_detalle_pedido automáticamente (DET-<id_pedido>-<n>).
    """
    productos = form.getlist("item_producto")
    cantidades = form.getlist("item_cantidad")

    items = []
    contador = 0
    for id_producto, cantidad in zip(productos, cantidades):
        if not id_producto:
            continue
        contador += 1
        items.append(
            {
                "id_detalle_pedido": f"DET-{id_pedido}-{contador}",
                "id_producto": id_producto,
                "cantidad_solicitada": int(cantidad or 0),
            }
        )
    return items


@pedidos_bp.route("/")
def ver_pedidos():
    pedidos = pedido_service.obtener_todos_los_pedidos()
    return render_template("pedidos.html", pedidos=pedidos)


@pedidos_bp.route("/nuevo", methods=["GET", "POST"])
def crear_pedido_view():
    clientes = cliente_service.obtener_todos_los_clientes()
    productos = producto_service.obtener_todos_los_productos()

    if request.method == "POST":
        id_pedido = request.form.get("id_pedido")
        data = {
            "id_pedido": id_pedido,
            "id_cliente": request.form.get("id_cliente"),
            "observaciones": request.form.get("observaciones") or None,
            "items": _items_desde_form(request.form, id_pedido),
        }
        try:
            nuevo = pedido_service.crear_pedido(data)
            return redirect(
                url_for("pedidos_views.ver_pedido_detalle", id_pedido=nuevo.id_pedido)
            )
        except ValueError as e:
            return render_template(
                "pedido_form.html",
                clientes=clientes,
                productos=productos,
                error=str(e),
            ), 400

    return render_template(
        "pedido_form.html", clientes=clientes, productos=productos, error=None
    )


@pedidos_bp.route("/<string:id_pedido>")
def ver_pedido_detalle(id_pedido):
    pedido = pedido_service.obtener_pedido_por_id(id_pedido)
    if not pedido:
        abort(404)

    cliente = cliente_service.obtener_cliente_por_id(pedido.id_cliente)

    # Mapa id_producto -> nombre para mostrar nombres legibles en la tabla
    productos = {
        p.id_producto: p for p in producto_service.obtener_todos_los_productos()
    }

    return render_template(
        "pedido_detalle.html",
        pedido=pedido,
        cliente=cliente,
        productos=productos,
    )


@pedidos_bp.route("/<string:id_pedido>/verificar", methods=["POST"])
def verificar_pedido_view(id_pedido):
    """
    Ejecuta la verificación de stock (FEFO) desde la vista HTML.
    Si hay stock suficiente el pedido pasa a 'verificado' (y queda listo
    para facturar); si no, pasa a 'rechazado'. Vuelve al detalle mostrando
    el resultado.
    """
    observaciones = request.form.get("observaciones") or None
    pedido = pedido_service.obtener_pedido_por_id(id_pedido)
    if not pedido:
        abort(404)

    cliente = cliente_service.obtener_cliente_por_id(pedido.id_cliente)
    productos = {
        p.id_producto: p for p in producto_service.obtener_todos_los_productos()
    }

    try:
        pedido_service.verificar_pedido(id_pedido, observaciones)
    except ValueError as e:
        pedido = pedido_service.obtener_pedido_por_id(id_pedido)
        return render_template(
            "pedido_detalle.html",
            pedido=pedido,
            cliente=cliente,
            productos=productos,
            error=str(e),
        ), 400

    return redirect(url_for("pedidos_views.ver_pedido_detalle", id_pedido=id_pedido))
