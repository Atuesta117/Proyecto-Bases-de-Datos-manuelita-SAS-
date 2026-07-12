from app import db


class Cliente(db.Model):
    __tablename__ = "clientes"

    # --- Identificación ---
    id_cliente = db.Column(db.String(100), primary_key=True)
    tipo_documento = db.Column(db.String(5), nullable=False)
    numero_identificacion = db.Column(db.String(20), nullable=False, unique=True)
    nombre_razon_social = db.Column(db.String(150), nullable=False)

    # --- Contacto ---
    email = db.Column(db.String(150), nullable=False, unique=True)
    telefono = db.Column(db.String(20))
    ciudad = db.Column(db.String(100), nullable=False)
    direccion_residencia = db.Column(db.String(255))
    direccion_operativa = db.Column(db.String(255))
    representante_legal = db.Column(db.String(150))

    # --- Datos legales / tributarios ---
    habeas_data = db.Column(db.Boolean, nullable=False, default=False)
    tipo_regimen = db.Column(
        db.String(25), nullable=False, default="no_responsable_iva"
    )

    # --- Metadata ---
    fecha_registro = db.Column(db.Date, nullable=False, default=db.func.current_date())

    # opcional
    def __repr__(self):
        return f"<Cliente {self.id_cliente} - {self.nombre_razon_social}>"
