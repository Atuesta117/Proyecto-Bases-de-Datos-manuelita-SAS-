from flask import render_template, Blueprint

bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@bp.route('/')
def listar():
    return render_template('clientes.html')