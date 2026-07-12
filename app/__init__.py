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

    # Importamos los Blueprints
    from app.routes.clientes_routes import clientes_bp
    from app.routes.proveedores_routes import proveedores_bp

    # Registramos los Blueprints en la app de Flask
    app.register_blueprint(clientes_bp)
    app.register_blueprint(proveedores_bp)

    return app