from flask import Blueprint, render_template, request, redirect, url_for, abort
from app.services import proveedor_service
from app.models.proveedor import Proveedor
import re

proveedores_bp = Blueprint("proveedores", __name__, url_prefix="/proveedores")


def generar_siguiente_id_proveedor():
    """
    Busca el último ID de pedido con formato PED-XXXXXX en la base de datos,
    extrae el número, le suma 1 y formatea el nuevo ID (ej: PED-002002).
    """
    # Buscamos todos los IDs que empiecen con "PED-"
    pedidos = Proveedor.query.filter(Proveedor.id_proveedor.like("PROV-%")).all()

    if not pedidos:
        return "PROV-000001"

    max_numero = 0
    for p in pedidos:
        # Extraemos solo la parte numérica usando una expresión regular
        match = re.match(r"PROV-(\d+)", p.id_proveedor)
        if match:
            numero = int(match.group(1))
            if numero > max_numero:
                max_numero = numero

    siguiente_numero = max_numero + 1
    # Formatea con ceros a la izquierda para garantizar un ancho de 6 dígitos
    return f"PED-{siguiente_numero:06d}"


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
            # Si ocurre un error, recalculamos el ID sugerido para volver a renderizar el formulario
            siguiente_id = generar_siguiente_id_proveedor()
            return render_template(
                "proveedor_form.html",
                proveedor=None,
                siguiente_id=siguiente_id,
                error=str(e),
            ), 400

    # Carga inicial (GET): calculamos el ID sugerido
    siguiente_id = generar_siguiente_id_proveedor()
    return render_template(
        "proveedor_form.html", proveedor=None, siguiente_id=siguiente_id, error=None
    )


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
