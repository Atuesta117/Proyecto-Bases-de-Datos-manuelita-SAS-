from app import db
from app.models.proveedor import Proveedor  # Asegúrate de mapear tu modelo aquí
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


def obtener_todos_los_proveedores():
    return Proveedor.query.all()


def obtener_proveedor_por_id(id_proveedor):
    return Proveedor.query.get(id_proveedor)


def crear_proveedor(data):
    nuevo = Proveedor(
        id_proveedor=data["id_proveedor"],
        nombre_razon_social=data["nombre_razon_social"],
        tipo_documento=data["tipo_documento"],
        numero_identificacion=data["numero_identificacion"],
        habeas_data=data.get("habeas_data", False),
        ciudad=data.get("ciudad", "Cali"),
        direccion_operativa=data.get("direccion_operativa"),
        direccion_residencia=data.get("direccion_residencia"),
        email=data["email"],
        num_contacto=data.get("num_contacto"),
        tipo_num_contacto=data.get("tipo_num_contacto"),
        representante_legal=data.get("representante_legal"),
        tipo_regimen=data.get("tipo_regimen", "no_responsable_iva"),
        rut=data["rut"],
        banco=data.get("banco"),
        tipo_cuenta=data.get("tipo_cuenta"),
        numero_cuenta=data.get("numero_cuenta"),
        tipo_proveedor=data.get("tipo_proveedor", "materia_prima"),
        tiempo_entrega_promedio=data.get("tiempo_entrega_promedio", 0),
        contacto_comercial=data.get("contacto_comercial"),
        contacto_cartera=data.get("contacto_cartera"),
        contacto_logistico=data.get("contacto_logistico"),
        condiciones_pago=data.get("condiciones_pago", 30),
        calificacion=data.get("calificacion", 3),
    )
    db.session.add(nuevo)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        # Cubre violaciones de CHECK (tipo_documento, tipo_regimen, tipo_num_contacto, tipo_cuenta,
        # tiempo_entrega_promedio, condiciones_pago, calificacion) y UNIQUE (numero_identificacion, email, rut).
        raise ValueError(f"No se pudo crear el proveedor: {e.orig}") from e

    return nuevo


def actualizar_proveedor(id_proveedor, data):
    proveedor = Proveedor.query.get(id_proveedor)
    if proveedor is None:
        return None

    # numero_identificacion y rut son campos críticos: protegidos contra edición
    campos_editables = [
        "nombre_razon_social",
        "tipo_documento",  # El tipo de doc se edita si no cambia el número básico fiscal
        "habeas_data",
        "ciudad",
        "direccion_operativa",
        "direccion_residencia",
        "email",
        "num_contacto",
        "tipo_num_contacto",
        "representante_legal",
        "tipo_regimen",
        "banco",
        "tipo_cuenta",
        "numero_cuenta",
        "tipo_proveedor",
        "tiempo_entrega_promedio",
        "contacto_comercial",
        "contacto_cartera",
        "contacto_logistico",
        "condiciones_pago",
        "calificacion",
    ]

    for campo in campos_editables:
        if campo in data:
            setattr(proveedor, campo, data[campo])

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"No se pudo actualizar el proveedor: {e.orig}") from e

    return proveedor


def tiene_ordenes_asociadas(id_proveedor):
    resultado = db.session.execute(
        text("SELECT 1 FROM ordenes_pedido_proveedor WHERE id_proveedor = :id LIMIT 1"),
        {"id": id_proveedor},
    ).first()
    return resultado is not None


def tiene_productos_asociados(id_proveedor):
    resultado = db.session.execute(
        text("SELECT 1 FROM productos WHERE id_proveedor = :id LIMIT 1"),
        {"id": id_proveedor},
    ).first()
    return resultado is not None


def eliminar_proveedor(id_proveedor):
    proveedor = Proveedor.query.get(id_proveedor)
    if proveedor is None:
        return "no_encontrado"

    if tiene_ordenes_asociadas(id_proveedor):
        return "tiene_ordenes"

    if tiene_productos_asociados(id_proveedor):
        return "tiene_productos"

    db.session.delete(proveedor)
    try:
        db.session.commit()
    except IntegrityError:
        # Red de seguridad por si existen lotes u otras dependencias en cascada/restrict restrictivas
        db.session.rollback()
        return "tiene_registros_asociados"

    return "eliminado"
