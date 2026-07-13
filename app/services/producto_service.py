from app import db
from app.models.producto import Producto, StockProducto
from app.models.proveedor import Proveedor
from app.models.lote import Lote  # Asegúrate de tener tu modelo Lote importado
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


def obtener_todos_los_productos():
    # Por defecto, el frontend solo necesita ver los que están activos en el inventario
    return Producto.query.filter_by(activo=True).all()


def obtener_producto_por_id(id_producto):
    return Producto.query.get(id_producto)


def obtener_lotes_por_producto(id_producto):
    """Retorna los lotes activos de un producto específico para responder al frontend"""
    lotes = Lote.query.filter(
        Lote.id_producto == id_producto, Lote.cantidad_actual > 0
    ).all()
    return [
        {
            "id_lote": l.id_lote,
            "id_proveedor": l.id_proveedor,
            "id_sede": l.id_sede,
            "fecha_ingreso": l.fecha_ingreso.isoformat(),
            "fecha_vencimiento": l.fecha_vencimiento.isoformat(),
            "cantidad_inicial": l.cantidad_inicial,
            "cantidad_actual": l.cantidad_actual,
        }
        for l in lotes
    ]


def crear_producto(data):
    # --- Restricción obligatoria de la guía ---
    # "NO se pueden registrar insumos o productos de proveedores que no
    # hayan sido registrados previamente en la aplicación."
    proveedor = Proveedor.query.get(data["id_proveedor"])
    if not proveedor:
        raise ValueError(
            f"No se puede registrar el insumo: el proveedor "
            f"'{data['id_proveedor']}' no está registrado previamente."
        )

    # Evitamos duplicar el ID del producto/insumo (mensaje claro en vez de IntegrityError crudo)
    if Producto.query.get(data["id_producto"]):
        raise ValueError(
            f"Ya existe un producto/insumo registrado con el ID '{data['id_producto']}'."
        )

    nuevo_prod = Producto(
        id_producto=data["id_producto"],
        id_proveedor=data["id_proveedor"],
        id_tipo_iva=data["id_tipo_iva"],
        nombre=data["nombre"],
        descripcion=data.get("descripcion"),
        precio=data["precio"],
        categoria=data["categoria"],
        peso=data["peso"],
        unidad_medida=data.get("unidad_medida"),
        activo=True,
    )
    db.session.add(nuevo_prod)

    # Creamos su registro en la tabla de STOCKPRODUCTOS.
    # inventario_actual y demanda_diaria se piden como parte del registro
    # del insumo/producto (según la guía), con 0 como valor por defecto.
    nuevo_stock = StockProducto(
        id_stock=f"STK-{data['id_producto']}",
        id_producto=data["id_producto"],
        cantidad_disponible=data.get("inventario_actual", 0),
        cantidad_reservada=0,
        stock_minimo=data.get("stock_minimo", 10),
        demanda_diaria=data.get("demanda_diaria", 0.0),
    )
    db.session.add(nuevo_stock)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"Error de integridad en base de datos: {e.orig}")

    return nuevo_prod


def actualizar_producto(id_producto, data):
    producto = Producto.query.get(id_producto)
    if not producto:
        return None

    # NO editamos 'id_producto' ni 'id_proveedor' (por consistencia histórica contable)
    campos_editables_prod = [
        "nombre",
        "descripcion",
        "precio",
        "categoria",
        "peso",
        "unidad_medida",
    ]
    for campo in campos_editables_prod:
        if campo in data:
            setattr(producto, campo, data[campo])

    # Si se actualizan variables de stock asociadas
    if producto.stock:
        if "inventario_actual" in data:
            producto.stock.cantidad_disponible = data["inventario_actual"]
        if "stock_minimo" in data:
            producto.stock.stock_minimo = data["stock_minimo"]
        if "demanda_diaria" in data:
            producto.stock.demanda_diaria = data["demanda_diaria"]

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"Error al actualizar: {e.orig}")

    return producto


def eliminar_logico_producto(id_producto):
    """Cumple con el enunciado: Pone el atributo activo en False"""
    producto = Producto.query.get(id_producto)
    if not producto:
        return False

    producto.activo = False
    db.session.commit()
    return True


def sumar_stock_disponible(id_producto, cantidad):
    """Suma unidades al inventario disponible cuando llega mercancía nueva"""
    producto = Producto.query.get(id_producto)
    if not producto or not producto.stock:
        return False

    # Sumamos las nuevas unidades al stock general de la tabla STOCKPRODUCTOS
    producto.stock.cantidad_disponible += cantidad
    return True
