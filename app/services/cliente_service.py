from app import db
from app.models.cliente import Cliente
from sqlalchemy import text


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
        telefono=data.get("telefono"),
        ciudad=data["ciudad"],
        direccion_residencia=data.get("direccion_residencia"),
        direccion_operativa=data.get("direccion_operativa"),
        representante_legal=data.get("representante_legal"),
        habeas_data=data.get("habeas_data", False),
        tipo_regimen=data.get("tipo_regimen", "no_responsable_iva"),
    )
    db.session.add(nuevo)
    db.session.commit()
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
        "telefono",
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

    db.session.commit()
    return cliente


def tiene_facturas_asociadas(id_cliente):
    resultado = db.session.execute(
        text("SELECT 1 FROM facturas WHERE id_cliente = :id LIMIT 1"),
        {"id": id_cliente},
    ).first()
    return resultado is not None


def eliminar_cliente(id_cliente):
    cliente = Cliente.query.get(id_cliente)
    if cliente is None:
        return "no_encontrado"

    if tiene_facturas_asociadas(id_cliente):
        return "tiene_facturas"

    db.session.delete(cliente)
    db.session.commit()
    return "eliminado"
