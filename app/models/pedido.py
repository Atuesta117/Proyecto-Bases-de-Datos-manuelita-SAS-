from app import db
from datetime import datetime, date


class Pedido(db.Model):
    __tablename__ = "pedido"

    id_pedido = db.Column(db.String(100), primary_key=True)
    id_cliente = db.Column(
        db.String(100), db.ForeignKey("clientes.id_cliente"), nullable=False
    )
    fecha_pedido = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # CHECK real en BD: 'pendiente','verificado','confirmado','rechazado','anulado'
    estado = db.Column(db.String(20), nullable=False, default="pendiente")
    observaciones = db.Column(db.Text)

    detalles = db.relationship(
        "DetallePedido", backref="pedido", cascade="all, delete-orphan", lazy=True
    )
    verificacion = db.relationship(
        "VerificarPedido", backref="pedido", uselist=False, cascade="all, delete-orphan"
    )

    def to_dict(self, incluir_detalles=True):
        data = {
            "id_pedido": self.id_pedido,
            "id_cliente": self.id_cliente,
            "fecha_pedido": self.fecha_pedido.isoformat(),
            "estado": self.estado,
            "observaciones": self.observaciones,
        }
        if incluir_detalles:
            data["detalles"] = [d.to_dict() for d in self.detalles]
        return data


class DetallePedido(db.Model):
    __tablename__ = "detalle_pedido"

    id_detalle_pedido = db.Column(db.String(100), primary_key=True)
    id_pedido = db.Column(
        db.String(100), db.ForeignKey("pedido.id_pedido"), nullable=False
    )
    id_producto = db.Column(
        db.String(100), db.ForeignKey("productos.id_producto"), nullable=False
    )
    cantidad_solicitada = db.Column(db.Integer, nullable=False)

    asignaciones_lote = db.relationship(
        "DetallePedidoLote",
        backref="detalle_pedido",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def to_dict(self):
        return {
            "id_detalle_pedido": self.id_detalle_pedido,
            "id_pedido": self.id_pedido,
            "id_producto": self.id_producto,
            "cantidad_solicitada": self.cantidad_solicitada,
        }


class VerificarPedido(db.Model):
    __tablename__ = "verificar_pedido"

    id_verificacion = db.Column(db.String(100), primary_key=True)
    id_pedido = db.Column(
        db.String(100), db.ForeignKey("pedido.id_pedido"), unique=True, nullable=False
    )
    fecha_verificacion = db.Column(db.Date, nullable=False, default=date.today)

    # OJO: en el SQL la columna se escribió "esValido" sin comillas,
    # así que Postgres la guarda en minúsculas: "esvalido".
    es_valido = db.Column("esvalido", db.Boolean, nullable=False)
    observaciones = db.Column(db.Text)

    def to_dict(self):
        return {
            "id_verificacion": self.id_verificacion,
            "id_pedido": self.id_pedido,
            "fecha_verificacion": self.fecha_verificacion.isoformat(),
            "es_valido": self.es_valido,
            "observaciones": self.observaciones,
        }


class DetallePedidoLote(db.Model):
    __tablename__ = "detalle_pedido_lote"

    id_asignacion = db.Column(db.String(100), primary_key=True)
    id_detalle_pedido = db.Column(
        db.String(100),
        db.ForeignKey("detalle_pedido.id_detalle_pedido"),
        nullable=False,
    )
    id_lote = db.Column(db.String(100), db.ForeignKey("lotes.id_lote"), nullable=False)
    cantidad_asignada = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id_asignacion": self.id_asignacion,
            "id_detalle_pedido": self.id_detalle_pedido,
            "id_lote": self.id_lote,
            "cantidad_asignada": self.cantidad_asignada,
        }
