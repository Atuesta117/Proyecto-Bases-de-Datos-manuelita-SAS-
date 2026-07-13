from flask import Blueprint, render_template, request, redirect, url_for, abort
from app.services import proveedor_service

proveedores_bp = Blueprint("proveedores", __name__, url_prefix="/proveedores")


def _form_a_dict(form):
    return {
        "id_proveedor": form.get("id_proveedor"),
        "nombre_razon_social": form.get("nombre_razon_social"),
        "tipo_documento": form.get("tipo_documento"),
        "numero_identificacion": form.get("numero_identificacion"),
        "email": form.get("email"),
        "rut": form.get("rut"),
        "ciudad": form.get("ciudad", "Cali"),
        "num_contacto": form.get("num_contacto") or None,
        "tipo_num_contacto": form.get("tipo_num_contacto") or None,
        "direccion_residencia": form.get("direccion_residencia") or None,
        "direccion_operativa": form.get("direccion_operativa") or None,
        "representante_legal": form.get("representante_legal") or None,
        "habeas_data": form.get("habeas_data") == "on",
        "tipo_regimen": form.get("tipo_regimen", "no_responsable_iva"),
        "banco": form.get("banco") or None,
        "tipo_cuenta": form.get("tipo_cuenta") or None,
        "numero_cuenta": form.get("numero_cuenta") or None,
        "tipo_proveedor": form.get("tipo_proveedor", "materia_prima"),
        "tiempo_entrega_promedio": int(form.get("tiempo_entrega_promedio") or 0),
        "condiciones_pago": int(form.get("condiciones_pago") or 30),
        "calificacion": int(form.get("calificacion") or 3),
        "contacto_comercial": form.get("contacto_comercial") or None,
        "contacto_cartera": form.get("contacto_cartera") or None,
        "contacto_logistico": form.get("contacto_logistico") or None,
    }


@proveedores_bp.route("/")
def ver_proveedores():
    proveedores = proveedor_service.obtener_todos_los_proveedores()
    return render_template("proveedores.html", proveedores=proveedores)


@proveedores_bp.route("/nuevo", methods=["GET", "POST"])
def crear_proveedor_view():
    if request.method == "POST":
        data = _form_a_dict(request.form)
        try:
            nuevo = proveedor_service.crear_proveedor(data)
            return redirect(
                url_for(
                    "proveedores.ver_proveedor_detalle", id_proveedor=nuevo.id_proveedor
                )
            )
        except ValueError as e:
            return render_template(
                "proveedor_form.html", proveedor=None, error=str(e)
            ), 400

    return render_template("proveedor_form.html", proveedor=None, error=None)


@proveedores_bp.route("/<string:id_proveedor>")
def ver_proveedor_detalle(id_proveedor):
    proveedor = proveedor_service.obtener_proveedor_por_id(id_proveedor)
    if not proveedor:
        abort(404)
    return render_template("proveedor_detalle.html", proveedor=proveedor)


@proveedores_bp.route("/<string:id_proveedor>/editar", methods=["GET", "POST"])
def editar_proveedor_view(id_proveedor):
    proveedor = proveedor_service.obtener_proveedor_por_id(id_proveedor)
    if not proveedor:
        abort(404)

    if request.method == "POST":
        # numero_identificacion y rut van deshabilitados en el formulario
        # (campos críticos protegidos); el servicio los ignora aunque
        # vengan en el dict.
        data = _form_a_dict(request.form)
        try:
            proveedor_service.actualizar_proveedor(id_proveedor, data)
            return redirect(
                url_for("proveedores.ver_proveedor_detalle", id_proveedor=id_proveedor)
            )
        except ValueError as e:
            return render_template(
                "proveedor_form.html", proveedor=proveedor, error=str(e)
            ), 400

    return render_template("proveedor_form.html", proveedor=proveedor, error=None)
