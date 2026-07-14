from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(Config)
    db.init_app(app)

    # Importamos TODOS los modelos aquí (antes de los blueprints) para que
    # SQLAlchemy pueda resolver las relaciones declaradas por string
    # (ej. db.relationship("Proveedor", ...)) sin importar en qué orden
    # se hayan definido los archivos.
    with app.app_context():
        from app.models import cliente, proveedor, producto, tipo_iva  # noqa: F401
        from app.models import orden_proveedor, lote  # noqa: F401
        from app.models import pedido, factura, logistica  # noqa: F401

    # --- Blueprints de API JSON (para Postman / frontend por fetch) ---
    from app.routes.clientes_routes import clientes_api_bp
    from app.routes.proveedores_routes import proveedores_api_bp
    from app.routes.productos_routes import productos_api_bp
    from app.routes.ordenes_routes import ordenes_api_bp
    from app.routes.pedidos_routes import pedidos_api_bp
    from app.routes.facturas_routes import facturas_api_bp
    from app.routes.camion_routes import camiones_api_bp
    from app.routes.conductor_routes import conductores_api_bp
    from app.routes.envio_routes import envios_api_bp

    app.register_blueprint(clientes_api_bp)
    app.register_blueprint(proveedores_api_bp)
    app.register_blueprint(productos_api_bp)
    app.register_blueprint(ordenes_api_bp)
    app.register_blueprint(pedidos_api_bp)
    app.register_blueprint(facturas_api_bp)
    app.register_blueprint(camiones_api_bp)
    app.register_blueprint(conductores_api_bp)
    app.register_blueprint(envios_api_bp)

    # --- Blueprints de vistas HTML (server-side, Jinja) ---
    from app.routes.clientes_views import clientes_bp
    from app.routes.proveedores_views import proveedores_bp
    from app.routes.productos_views import productos_bp
    from app.routes.ordenes_views import ordenes_vistas_bp
    from app.routes.pedidos_views import pedidos_bp
    from app.routes.facturas_views import facturas_bp
    from app.routes.camion_views import camiones_bp
    from app.routes.conductor_views import conductores_bp
    from app.routes.envio_views import envios_bp

    app.register_blueprint(clientes_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(ordenes_vistas_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(facturas_bp)
    app.register_blueprint(camiones_bp)
    app.register_blueprint(conductores_bp)
    app.register_blueprint(envios_bp)

    # --- Ruta de inicio ---
    from flask import render_template

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
