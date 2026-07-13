from app import db


class TipoIva(db.Model):
    __tablename__ = "tipos_iva"

    id_tipo_iva = db.Column(db.String(100), primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    porcentaje = db.Column(db.Numeric(5, 2), nullable=False)

    def to_dict(self):
        return {
            "id_tipo_iva": self.id_tipo_iva,
            "nombre": self.nombre,
            "porcentaje": float(self.porcentaje),
        }
