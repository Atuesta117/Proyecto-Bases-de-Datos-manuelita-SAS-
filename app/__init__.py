from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Importamos los Blueprints
    from app.routes.clientes_routes import clientes_bp
    from app.routes.proveedores_routes import proveedores_bp
    from app.routes.productos_routes import productos_bp
    from app.routes.ordenes_routes import ordenes_bp

    # Registramos los Blueprints en la app de Flask
    app.register_blueprint(clientes_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(ordenes_bp)

    return app
