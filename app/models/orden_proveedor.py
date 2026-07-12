from app import db
from datetime import date


class OrdenPedidoProveedor(db.Model):
    __tablename__ = "ordenes_pedido_proveedor"

    id_orden = db.Column(db.String(100), primary_key=True)
    numero_orden = db.Column(
        db.BigInteger, unique=True
    )  # lo llena BIGSERIAL, no lo seteamos

    id_sede = db.Column(db.String(100), db.ForeignKey("sedes.id_sede"), nullable=False)
    id_proveedor = db.Column(
        db.String(100), db.ForeignKey("proveedores.id_proveedor"), nullable=False
    )

    fecha_pedido = db.Column(db.Date, nullable=False, default=date.today)
    lugar_entrega = db.Column(db.String(255), nullable=False)

    # OJO: minúsculas, tal como exige el CHECK de la tabla
    ESTADOS_VALIDOS = ("pendiente", "en_transito", "recibido", "cancelado")
    estado = db.Column(db.String(20), nullable=False, default="pendiente")

    detalles = db.relationship(
        "DetalleOrdenPedidoProveedor",
        backref="orden",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def to_dict(self):
        return {
            "id_orden": self.id_orden,
            "numero_orden": self.numero_orden,
            "id_sede": self.id_sede,
            "id_proveedor": self.id_proveedor,
            "fecha_pedido": self.fecha_pedido.isoformat(),
            "lugar_entrega": self.lugar_entrega,
            "estado": self.estado,
            "detalles": [d.to_dict() for d in self.detalles],
        }


class DetalleOrdenPedidoProveedor(db.Model):
    __tablename__ = "detalle_orden_pedido_proveedor"

    id_detalle_orden = db.Column(db.String(100), primary_key=True)
    id_orden = db.Column(
        db.String(100),
        db.ForeignKey("ordenes_pedido_proveedor.id_orden"),
        nullable=False,
    )
    id_producto = db.Column(
        db.String(100), db.ForeignKey("productos.id_producto"), nullable=False
    )
    cantidad = db.Column(db.Integer, nullable=False)
    costo_unitario = db.Column(db.BigInteger, nullable=False)

    def to_dict(self):
        return {
            "id_detalle_orden": self.id_detalle_orden,
            "id_orden": self.id_orden,
            "id_producto": self.id_producto,
            "cantidad": self.cantidad,
            "costo_unitario": self.costo_unitario,
        }
