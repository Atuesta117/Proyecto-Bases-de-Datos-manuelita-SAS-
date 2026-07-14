from flask import Blueprint, render_template, request, redirect, url_for, abort
from app.services import producto_service
from app.services import proveedor_service
from app.models.producto import Producto
import re

productos_bp = Blueprint("productos", __name__, url_prefix="/productos")


def generar_siguiente_id_producto():
    """
    Busca el último ID de pedido con formato PED-XXXXXX en la base de datos,
    extrae el número, le suma 1 y formatea el nuevo ID (ej: PED-002002).
    """
    # Buscamos todos los IDs que empiecen con "PED-"
    pedidos = Producto.query.filter(Producto.id_producto.like("PROD-%")).all()

    if not pedidos:
        return "PROD-000001"

    max_numero = 0
    for p in pedidos:
        # Extraemos solo la parte numérica usando una expresión regular
        match = re.match(r"PROD-(\d+)", p.id_producto)
        if match:
            numero = int(match.group(1))
            if numero > max_numero:
                max_numero = numero

    siguiente_numero = max_numero + 1
    # Formatea con ceros a la izquierda para garantizar un ancho de 6 dígitos
    return f"PROD-{siguiente_numero:06d}"


# --- Reglas de negocio: Días de Stock (NO se almacena, se calcula al vuelo) ---
# Fórmula: Días de stock = Inventario actual / Demanda diaria
def calcular_estado_inventario(cantidad_disponible, demanda_diaria):
    """Devuelve dias_stock, categoria y acción recomendada según la tabla de la guía:
    0 días -> AGOTADO -> Pedido Inmediato
    < 5 días -> CRÍTICO -> Pedido de Emergencia
    5-15 días -> ALERTA -> Realizar Pedido Normal
    > 15 días -> SEGURO -> Mantener Monitoreo
    """
    if cantidad_disponible is None:
        cantidad_disponible = 0
    if not demanda_diaria:
        return {
            "dias_stock": None,
            "categoria": "SIN DEMANDA",
            "categoria_slug": "sin-demanda",
            "accion": "Registrar demanda diaria para calcular el estado",
        }

    dias_stock = cantidad_disponible / demanda_diaria

    if cantidad_disponible <= 0 or dias_stock == 0:
        categoria, slug, accion = "AGOTADO", "agotado", "Pedido Inmediato"
    elif dias_stock < 5:
        categoria, slug, accion = "CRÍTICO", "critico", "Pedido de Emergencia"
    elif dias_stock <= 15:
        categoria, slug, accion = "ALERTA", "alerta", "Realizar Pedido Normal"
    else:
        categoria, slug, accion = "SEGURO", "seguro", "Mantener Monitoreo"

    return {
        "dias_stock": round(dias_stock, 1),
        "categoria": categoria,
        "categoria_slug": slug,
        "accion": accion,
    }


def _form_a_dict(form):
    def _num(campo, tipo, default=None):
        valor = form.get(campo)
        if valor in (None, ""):
            return default
        return tipo(valor)

    return {
        "id_producto": form.get("id_producto"),
        "id_proveedor": form.get("id_proveedor"),
        "id_tipo_iva": form.get("id_tipo_iva"),
        "nombre": form.get("nombre"),
        "descripcion": form.get("descripcion") or None,
        "precio": _num("precio", float, 0.0),
        "categoria": form.get("categoria"),
        "peso": _num("peso", float, 0.0),
        "unidad_medida": form.get("unidad_medida") or None,
        # Datos de stock (se piden en el registro, según la guía)
        "inventario_actual": _num("inventario_actual", int, 0),
        "stock_minimo": _num("stock_minimo", int, 10),
        "demanda_diaria": _num("demanda_diaria", float, 0.0),
    }


@productos_bp.route("/")
def ver_productos():
    productos = producto_service.obtener_todos_los_productos()

    productos_con_estado = []
    for p in productos:
        stock = getattr(p, "stock", None)
        cantidad_disponible = stock.cantidad_disponible if stock else 0
        demanda_diaria = stock.demanda_diaria if stock else 0
        estado = calcular_estado_inventario(cantidad_disponible, demanda_diaria)
        productos_con_estado.append(
            {
                "producto": p,
                "cantidad_disponible": cantidad_disponible,
                "estado": estado,
            }
        )

    return render_template("productos.html", productos=productos_con_estado)


@productos_bp.route("/nuevo", methods=["GET", "POST"])
def crear_producto_view():
    proveedores = proveedor_service.obtener_todos_los_proveedores()

    if request.method == "POST":
        data = _form_a_dict(request.form)
        try:
            nuevo = producto_service.crear_producto(data)
            return redirect(
                url_for("productos.ver_producto_detalle", id_producto=nuevo.id_producto)
            )
        except ValueError as e:
            siguiente_id = generar_siguiente_id_producto()
            return render_template(
                "producto_form.html",
                producto=None,
                proveedores=proveedores,
                siguiente_id=siguiente_id,  # <-- Enviamos el ID aquí en caso de error
                error=str(e),
            ), 400

    siguiente_id = generar_siguiente_id_producto()
    return render_template(
        "producto_form.html",
        producto=None,
        proveedores=proveedores,
        siguiente_id=siguiente_id,  # <-- Enviamos el ID aquí
        error=None,
    )


@productos_bp.route("/<string:id_producto>")
def ver_producto_detalle(id_producto):
    producto = producto_service.obtener_producto_por_id(id_producto)
    if not producto:
        abort(404)

    stock = getattr(producto, "stock", None)
    cantidad_disponible = stock.cantidad_disponible if stock else 0
    demanda_diaria = stock.demanda_diaria if stock else 0
    estado = calcular_estado_inventario(cantidad_disponible, demanda_diaria)

    lotes = producto_service.obtener_lotes_por_producto(id_producto)

    return render_template(
        "producto_detalle.html",
        producto=producto,
        stock=stock,
        estado=estado,
        lotes=lotes,
    )


@productos_bp.route("/<string:id_producto>/editar", methods=["GET", "POST"])
def editar_producto_view(id_producto):
    producto = producto_service.obtener_producto_por_id(id_producto)
    if not producto:
        abort(404)

    proveedores = proveedor_service.obtener_todos_los_proveedores()

    if request.method == "POST":
        # id_producto e id_proveedor van deshabilitados en el formulario
        # (campos críticos protegidos por consistencia histórica contable);
        # el servicio solo aplica los campos editables permitidos.
        data = _form_a_dict(request.form)
        try:
            producto_service.actualizar_producto(id_producto, data)
            return redirect(
                url_for("productos.ver_producto_detalle", id_producto=id_producto)
            )
        except ValueError as e:
            return render_template(
                "producto_form.html",
                producto=producto,
                proveedores=proveedores,
                error=str(e),
            ), 400

    return render_template(
        "producto_form.html", producto=producto, proveedores=proveedores, error=None
    )

