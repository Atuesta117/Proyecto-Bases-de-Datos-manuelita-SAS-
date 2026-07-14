from flask import Blueprint, render_template, request, redirect, url_for, abort
from app.services import camion_service
import re
from app.models.logistica import Camion

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
    extrae el número, le suma 1 y formatea el nuevo ID sugerido (ej: CAM-000045).
    """
    # Buscamos todos los camiones cuyo ID comience con "CAM-"
    camiones = Camion.query.filter(Camion.id_camion.like("CAM-%")).all()

    if not camiones:
        return "CAM-000001"

    max_numero = 0
    for c in camiones:
        # Extraemos la sección numérica secuencial de 6 dígitos
        match = re.match(r"CAM-(\d+)", c.id_camion)
        if match:
            numero = int(match.group(1))
            if numero > max_numero:
                max_numero = numero

    siguiente_numero = max_numero + 1
    # Formatea con ceros a la izquierda garantizando un ancho fijo de 6 dígitos
    return f"CAM-{siguiente_numero:06d}"


@camiones_bp.route("/")
def ver_camiones():
    camiones = camion_service.obtener_todos_los_camiones()
    return render_template("camiones.html", camiones=camiones)


@camiones_bp.route("/nuevo", methods=["GET", "POST"])
def crear_camion_view():
    if request.method == "POST":
        data = _form_a_dict(request.form)
        try:
            nuevo = camion_service.crear_camion(data)
            return redirect(
                url_for("camiones.ver_camion_detalle", id_camion=nuevo.id_camion)
            )
        except ValueError as e:
            # Si ocurre un error, recalculamos el ID sugerido para renderizar nuevamente
            siguiente_id = generar_siguiente_id_camion()
            return render_template(
                "camion_form.html",
                camion=None,
                siguiente_id=siguiente_id,
                error=str(e)
            ), 400

    # Carga inicial (GET): calculamos el ID secuencial sugerido
    siguiente_id = generar_siguiente_id_camion()
    return render_template(
        "camion_form.html",
        camion=None,
        siguiente_id=siguiente_id,
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

    if request.method == "POST":
        # placa va deshabilitada en el formulario (campo crítico protegido);
        # el servicio la ignora aunque venga en el dict, así que no hace
        # falta filtrarla aquí.
        data = _form_a_dict(request.form)
        try:
            camion_service.actualizar_camion(id_camion, data)
            return redirect(
                url_for("camiones.ver_camion_detalle", id_camion=id_camion)
            )
        except ValueError as e:
            return render_template(
                "camion_form.html", camion=camion, error=str(e)
            ), 400

    return render_template("camion_form.html", camion=camion, error=None)
