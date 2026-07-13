from flask import Blueprint, render_template, request, redirect, url_for, abort
from app.services import cliente_service

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")


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
            return render_template("cliente_form.html", cliente=None, error=str(e)), 400

    return render_template("cliente_form.html", cliente=None, error=None)


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
