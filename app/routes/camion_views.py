from flask import Blueprint, render_template, request, redirect, url_for, abort
from app.services import camion_service
import re
from app.models.logistica import Camion, Sedes # Se importa Sedes de logistica

camiones_bp = Blueprint("camiones", __name__, url_prefix="/camiones")


def _form_a_dict(form):
    """Convierte el formulario HTML en el dict que esperan los servicios."""
    return {
        "id_camion": form.get("id_camion"),
        "placa": form.get("placa"),
        "marca": form.get("marca"),
        "modelo": form.get("modelo"),
        "capacidad_kg": form.get("capacidad_kg"),
        "estado": form.get("estado", "disponible"),
        "kilometraje": form.get("kilometraje") or 0,
        "id_sede": form.get("id_sede") or None,
    }

def generar_siguiente_id_camion():
    """
    Busca el último ID de camión con formato CAM-XXXXXX en la base de datos,
    extrae el número, le suma 1 y formatea el nuevo ID sugerido.
    """
    camiones = Camion.query.filter(Camion.id_camion.like("CAM-%")).all()

    if not camiones:
        return "CAM-000001"

    max_numero = 0
    for c in camiones:
        match = re.match(r"CAM-(\d+)", c.id_camion)
        if match:
            numero = int(match.group(1))
            if numero > max_numero:
                max_numero = numero

    siguiente_numero = max_numero + 1
    return f"CAM-{siguiente_numero:06d}"


@camiones_bp.route("/")
def ver_camiones():
    camiones = camion_service.obtener_todos_los_camiones()
    return render_template("camiones.html", camiones=camiones)


@camiones_bp.route("/nuevo", methods=["GET", "POST"])
def crear_camion_view():
    # Obtenemos la lista de todas las sedes para el desplegable
    sedes = Sedes.query.all()

    if request.method == "POST":
        data = _form_a_dict(request.form)
        try:
            nuevo = camion_service.crear_camion(data)
            return redirect(
                url_for("camiones.ver_camion_detalle", id_camion=nuevo.id_camion)
            )
        except ValueError as e:
            siguiente_id = generar_siguiente_id_camion()
            return render_template(
                "camion_form.html",
                camion=None,
                siguiente_id=siguiente_id,
                sedes=sedes,
                error=str(e)
            ), 400

    siguiente_id = generar_siguiente_id_camion()
    return render_template(
        "camion_form.html",
        camion=None,
        siguiente_id=siguiente_id,
        sedes=sedes,
        error=None
    )


@camiones_bp.route("/<string:id_camion>")
def ver_camion_detalle(id_camion):
    camion = camion_service.obtener_camion_por_id(id_camion)
    if not camion:
        abort(404)
    return render_template("camion_detalle.html", camion=camion)


@camiones_bp.route("/<string:id_camion>/editar", methods=["GET", "POST"])
def editar_camion_view(id_camion):
    camion = camion_service.obtener_camion_por_id(id_camion)
    if not camion:
        abort(404)

    sedes = Sedes.query.all()

    if request.method == "POST":
        data = _form_a_dict(request.form)
        try:
            camion_service.actualizar_camion(id_camion, data)
            return redirect(
                url_for("camiones.ver_camion_detalle", id_camion=id_camion)
            )
        except ValueError as e:
            return render_template(
                "camion_form.html",
                camion=camion,
                sedes=sedes,
                error=str(e)
            ), 400

    return render_template("camion_form.html", camion=camion, sedes=sedes, error=None)