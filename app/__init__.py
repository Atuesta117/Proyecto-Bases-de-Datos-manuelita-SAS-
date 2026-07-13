from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy()


def create_app():
    # Especifica las rutas de templates y static
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(Config)
    db.init_app(app)
    @app.route('/')
    def index():
        return render_template('index.html')

    # Importamos TODOS los modelos aquí (antes de los blueprints) para que
    # SQLAlchemy pueda resolver las relaciones declaradas por string
    # (ej. db.relationship("Proveedor", ...)) sin importar en qué orden
    # se hayan definido los archivos.
    with app.app_context():
        from app.models import cliente, proveedor, producto, tipo_iva  # noqa: F401
        from app.models import orden_proveedor, lote  # noqa: F401
        from app.models import pedido, factura, logistica  # noqa: F401

    # Importamos los Blueprints
    from app.routes.clientes_routes import clientes_bp
    from app.routes.proveedores_routes import proveedores_bp
    from app.routes.productos_routes import productos_bp
    from app.routes.ordenes_routes import ordenes_bp
    from app.routes.pedidos_routes import pedidos_bp
    from app.routes.facturas_routes import facturas_bp

    # Registramos los Blueprints en la app de Flask
    app.register_blueprint(clientes_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(ordenes_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(facturas_bp)

    return app