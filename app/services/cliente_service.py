from app import db
from app.models.cliente import Cliente
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


def obtener_todos_los_clientes():
    return Cliente.query.all()


def obtener_cliente_por_id(id_cliente):
    return Cliente.query.get(id_cliente)


def crear_cliente(data):
    nuevo = Cliente(
        id_cliente=data["id_cliente"],
        tipo_documento=data["tipo_documento"],
        numero_identificacion=data["numero_identificacion"],
        nombre_razon_social=data["nombre_razon_social"],
        email=data["email"],
        num_contacto=data.get("num_contacto"),
        tipo_num_contacto=data.get("tipo_num_contacto"),
        ciudad=data.get("ciudad", "Cali"),
        direccion_residencia=data.get("direccion_residencia"),
        direccion_operativa=data.get("direccion_operativa"),
        representante_legal=data.get("representante_legal"),
        habeas_data=data.get("habeas_data", False),
        tipo_regimen=data.get("tipo_regimen", "no_responsable_iva"),
    )
    db.session.add(nuevo)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        # Cubre violaciones de CHECK (tipo_documento, tipo_regimen,
        # tipo_num_contacto) y de UNIQUE (numero_identificacion, email).
        raise ValueError(f"No se pudo crear el cliente: {e.orig}") from e

    return nuevo


def actualizar_cliente(id_cliente, data):
    cliente = Cliente.query.get(id_cliente)
    if cliente is None:
        return None

    # numero_identificacion es un campo crítico (como el NIT/Cédula):
    # no se toca aunque venga en el body de la petición.
    campos_editables = [
        "nombre_razon_social",
        "email",
        "num_contacto",
        "tipo_num_contacto",
        "ciudad",
        "direccion_residencia",
        "direccion_operativa",
        "representante_legal",
        "habeas_data",
        "tipo_regimen",
    ]
    for campo in campos_editables:
        if campo in data:
            setattr(cliente, campo, data[campo])

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"No se pudo actualizar el cliente: {e.orig}") from e

    return cliente


def tiene_facturas_asociadas(id_cliente):
    resultado = db.session.execute(
        text("SELECT 1 FROM facturas WHERE id_cliente = :id LIMIT 1"),
        {"id": id_cliente},
    ).first()
    return resultado is not None


def tiene_pedidos_asociados(id_cliente):
    # PEDIDO tiene FK RESTRICT hacia clientes: si un cliente tiene un
    # pedido (aunque nunca haya llegado a generar factura), Postgres
    # impedirá el DELETE. Lo validamos antes para dar un mensaje claro.
    resultado = db.session.execute(
        text("SELECT 1 FROM pedido WHERE id_cliente = :id LIMIT 1"),
        {"id": id_cliente},
    ).first()
    return resultado is not None


def eliminar_cliente(id_cliente):
    cliente = Cliente.query.get(id_cliente)
    if cliente is None:
        return "no_encontrado"

    if tiene_facturas_asociadas(id_cliente):
        return "tiene_facturas"

    if tiene_pedidos_asociados(id_cliente):
        return "tiene_pedidos"

    db.session.delete(cliente)
    try:
        db.session.commit()
    except IntegrityError:
        # Red de seguridad por si en el futuro se agrega otra tabla
        # con FK RESTRICT hacia clientes y se nos olvida validarla aquí.
        db.session.rollback()
        return "tiene_registros_asociados"

    return "eliminado"
