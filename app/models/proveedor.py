from app import db


class Proveedor(db.Model):
    __tablename__ = "proveedores"

    # Identificacion
    id_proveedor = db.Column(db.String(100), primary_key=True)
    nombre_razon_social = db.Column(db.String(100), nullable=False)
    tipo_documento = db.Column(db.String(5), nullable=False)  # CC, NIT, CE
    numero_identificacion = db.Column(db.String(20), nullable=False, unique=True)

    # Datos legales
    habeas_data = db.Column(db.Boolean, nullable=False, default=False)
    tipo_regimen = db.Column(
        db.String(25), nullable=False, default="no_responsable_iva"
    )  # responsable_iva / no_responsable_iva
    rut = db.Column(db.String(20), nullable=False, unique=True)

    # Contacto y Ubicación
    ciudad = db.Column(db.String(100), nullable=False, default="Cali")
    direccion_operativa = db.Column(db.String(255))
    direccion_residencia = db.Column(db.String(255))
    email = db.Column(db.String(150), nullable=False, unique=True)
    num_contacto = db.Column(db.String(20))
    tipo_num_contacto = db.Column(db.String(20))  # celular / telefono
    representante_legal = db.Column(db.String(150))

    # Datos Bancarios
    banco = db.Column(db.String(100))
    tipo_cuenta = db.Column(db.String(20))  # ahorros / corriente
    numero_cuenta = db.Column(db.String(30))

    # Información Comercial / Logística
    tipo_proveedor = db.Column(db.String(100), nullable=False, default="materia_prima")
    tiempo_entrega_promedio = db.Column(db.Integer, nullable=False, default=0)
    condiciones_pago = db.Column(db.Integer, nullable=False, default=30)
    calificacion = db.Column(db.SmallInteger, nullable=False, default=3)

    # Contactos Específicos
    contacto_comercial = db.Column(db.String(100))
    contacto_cartera = db.Column(db.String(100))
    contacto_logistico = db.Column(db.String(100))

    # Metadata
    fecha_registro = db.Column(db.Date, nullable=False, default=db.func.current_date())

    def to_dict(self):
        return {
            "id_proveedor": self.id_proveedor,
            "nombre_razon_social": self.nombre_razon_social,
            "tipo_documento": self.tipo_documento,
            "numero_identificacion": self.numero_identificacion,
            "habeas_data": self.habeas_data,
            "ciudad": self.ciudad,
            "direccion_operativa": self.direccion_operativa,
            "direccion_residencia": self.direccion_residencia,
            "email": self.email,
            "num_contacto": self.num_contacto,
            "tipo_num_contacto": self.tipo_num_contacto,
            "representante_legal": self.representante_legal,
            "tipo_regimen": self.tipo_regimen,
            "rut": self.rut,
            "banco": self.banco,
            "tipo_cuenta": self.tipo_cuenta,
            "numero_cuenta": self.numero_cuenta,
            "tipo_proveedor": self.tipo_proveedor,
            "tiempo_entrega_promedio": self.tiempo_entrega_promedio,
            "contacto_comercial": self.contacto_comercial,
            "contacto_cartera": self.contacto_cartera,
            "contacto_logistico": self.contacto_logistico,
            "condiciones_pago": self.condiciones_pago,
            "calificacion": self.calificacion,
            "fecha_registro": self.fecha_registro.isoformat()
            if self.fecha_registro
            else None,
        }

    def __repr__(self):
        return f"<Proveedor {self.id_proveedor} - {self.nombre_razon_social}>"
