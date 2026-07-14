from flask import Blueprint, render_template, request, redirect, url_for, abort
from app.services import conductor_service
from app import db
from sqlalchemy import text
import re
from app.models.logistica import Conductor

conductores_bp = Blueprint("conductores", __name__, url_prefix="/conductores")


def obtener_sedes_raw():
    """Obtiene las sedes directamente de la base de datos."""
    query = text("SELECT id_sede, nombre_sede, ciudad FROM SEDES")
    resultado = db.session.execute(query)
    return [
        {"id_sede": row.id_sede, "nombre_sede": row.nombre_sede, "ciudad": row.ciudad}
        for row in resultado
    ]


def _form_a_dict(form):
    """Convierte el formulario HTML en el dict que esperan los servicios."""
    return {
        "id_conductor": form.get("id_conductor"),
        "nombre": form.get("nombre"),
        "apellido": form.get("apellido"),
        "cedula": form.get("cedula"),
        "telefono": form.get("telefono"),
        "licencia": form.get("licencia"),
        "fecha_vencimiento_licencia": form.get("fecha_vencimiento_licencia"),
        "id_sede": form.get("id_sede") or None,
        "disponible": form.get("disponible") == "on",
    }

def generar_siguiente_id_conductor():
    """
    Busca el último ID de conductor con formato COND-XXXXXX en la base de datos,
    extrae el número, le suma 1 y formatea el nuevo ID sugerido (ej: COND-000045).
    """
    # Buscamos todos los conductores cuyo ID comience con "COND-"
    conductores = Conductor.query.filter(Conductor.id_conductor.like("COND-%")).all()

    if not conductores:
        return "COND-000001"

    max_numero = 0
    for c in conductores:
        # Extraemos la sección numérica secuencial de 6 dígitos
        match = re.match(r"COND-(\d+)", c.id_conductor)
        if match:
            numero = int(match.group(1))
            if numero > max_numero:
                max_numero = numero

    siguiente_numero = max_numero + 1
    # Formatea con ceros a la izquierda garantizando un ancho de 6 dígitos
    return f"COND-{siguiente_numero:06d}"


@conductores_bp.route("/")
def ver_conductores():
    conductores = conductor_service.obtener_todos_los_conductores()
    return render_template("conductores.html", conductores=conductores)


@conductores_bp.route("/nuevo", methods=["GET", "POST"])
def crear_conductor_view():
    sedes = obtener_sedes_raw() # Tu función de carga de sedes directas

    if request.method == "POST":
        data = _form_a_dict(request.form)
        try:
            nuevo = conductor_service.crear_conductor(data)
            return redirect(
                url_for(
                    "conductores.ver_conductor_detalle",
                    id_conductor=nuevo.id_conductor,
                )
            )
        except ValueError as e:
            # Recalculamos si hay un error para volver a pintar el formulario
            siguiente_id = generar_siguiente_id_conductor()
            return render_template(
                "conductor_form.html",
                conductor=None,
                siguiente_id=siguiente_id,
                sedes=sedes,
                error=str(e)
            ), 400

    # Carga inicial (GET): Generamos el ID consecutivo sugerido
    siguiente_id = generar_siguiente_id_conductor()
    return render_template(
        "conductor_form.html",
        conductor=None,
        siguiente_id=siguiente_id,
        sedes=sedes,
        error=None
    )


@conductores_bp.route("/<string:id_conductor>")
def ver_conductor_detalle(id_conductor):
    conductor = conductor_service.obtener_conductor_por_id(id_conductor)
    if not conductor:
        abort(404)
    return render_template("conductor_detalle.html", conductor=conductor)


@conductores_bp.route("/<string:id_conductor>/editar", methods=["GET", "POST"])
def editar_conductor_view(id_conductor):
    conductor = conductor_service.obtener_conductor_por_id(id_conductor)
    if not conductor:
        abort(404)

    sedes = obtener_sedes_raw()  # Cargamos las sedes de la BD

    if request.method == "POST":
        data = _form_a_dict(request.form)
        try:
            conductor_service.actualizar_conductor(id_conductor, data)
            return redirect(
                url_for("conductores.ver_conductor_detalle", id_conductor=id_conductor)
            )
        except ValueError as e:
            return render_template(
                "conductor_form.html",
                conductor=conductor,
                sedes=sedes,
                error=str(e)
            ), 400

    return render_template(
        "conductor_form.html",
        conductor=conductor,
        sedes=sedes,
        error=None
    )