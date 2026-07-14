from flask import Blueprint, render_template, request, redirect, url_for, abort
from app.services import cliente_service
import re
from app.models.cliente import Cliente

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")


def generar_siguiente_id_cliente():
    """
    Busca el último ID de pedido con formato PED-XXXXXX en la base de datos,
    extrae el número, le suma 1 y formatea el nuevo ID (ej: PED-002002).
    """
    # Buscamos todos los IDs que empiecen con "PED-"
    pedidos = Cliente.query.filter(Cliente.id_cliente.like("CLI-%")).all()

    if not pedidos:
        return "CLI-000001"

    max_numero = 0
    for p in pedidos:
        # Extraemos solo la parte numérica usando una expresión regular
        match = re.match(r"CLI-(\d+)", p.id_cliente)
        if match:
            numero = int(match.group(1))
            if numero > max_numero:
                max_numero = numero

    siguiente_numero = max_numero + 1
    # Formatea con ceros a la izquierda para garantizar un ancho de 6 dígitos
    return f"CLI-{siguiente_numero:06d}"


def _form_a_dict(form):
    """Convierte el formulario HTML en el dict que esperan los servicios."""
    return {
        "id_cliente": form.get("id_cliente"),
        "tipo_documento": form.get("tipo_documento"),
        "numero_identificacion": form.get("numero_identificacion"),
        "nombre_razon_social": form.get("nombre_razon_social"),
        "email": form.get("email"),
        "ciudad": form.get("ciudad", "Cali"),
        "num_contacto": form.get("num_contacto") or None,
        "tipo_num_contacto": form.get("tipo_num_contacto") or None,
        "direccion_residencia": form.get("direccion_residencia") or None,
        "direccion_operativa": form.get("direccion_operativa") or None,
        "representante_legal": form.get("representante_legal") or None,
        "habeas_data": form.get("habeas_data") == "on",
        "tipo_regimen": form.get("tipo_regimen", "no_responsable_iva"),
    }


@clientes_bp.route("/")
def ver_clientes():
    clientes = cliente_service.obtener_todos_los_clientes()
    return render_template("clientes.html", clientes=clientes)


@clientes_bp.route("/nuevo", methods=["GET", "POST"])
def crear_cliente_view():
    if request.method == "POST":
        data = _form_a_dict(request.form)
        try:
            nuevo = cliente_service.crear_cliente(data)
            return redirect(
                url_for("clientes.ver_cliente_detalle", id_cliente=nuevo.id_cliente)
            )
        except ValueError as e:
            # Si ocurre un error, recalculamos el ID sugerido para volver a renderizar el formulario
            siguiente_id = generar_siguiente_id_cliente()
            return render_template(
                "cliente_form.html",
                cliente=None,
                siguiente_id=siguiente_id,
                error=str(e),
            ), 400

    # Carga inicial (GET): calculamos el ID sugerido
    siguiente_id = generar_siguiente_id_cliente()
    return render_template(
        "cliente_form.html", cliente=None, siguiente_id=siguiente_id, error=None
    )


@clientes_bp.route("/<string:id_cliente>")
def ver_cliente_detalle(id_cliente):
    cliente = cliente_service.obtener_cliente_por_id(id_cliente)
    if not cliente:
        abort(404)
    return render_template("cliente_detalle.html", cliente=cliente)


@clientes_bp.route("/<string:id_cliente>/editar", methods=["GET", "POST"])
def editar_cliente_view(id_cliente):
    cliente = cliente_service.obtener_cliente_por_id(id_cliente)
    if not cliente:
        abort(404)

    if request.method == "POST":
        # numero_identificacion y tipo_documento van deshabilitados en el
        # formulario (campos críticos protegidos); el servicio los ignora
        # aunque vengan en el dict, así que no hace falta filtrarlos aquí.
        data = _form_a_dict(request.form)
        try:
            cliente_service.actualizar_cliente(id_cliente, data)
            return redirect(
                url_for("clientes.ver_cliente_detalle", id_cliente=id_cliente)
            )
        except ValueError as e:
            return render_template(
                "cliente_form.html", cliente=cliente, error=str(e)
            ), 400

    return render_template("cliente_form.html", cliente=cliente, error=None)
