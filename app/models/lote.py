from app import db


class Lote(db.Model):
    __tablename__ = "lotes"

    id_lote = db.Column(db.String(100), primary_key=True)

    id_producto = db.Column(
        db.String(100), db.ForeignKey("productos.id_producto"), nullable=False
    )
    id_proveedor = db.Column(
        db.String(100), db.ForeignKey("proveedores.id_proveedor"), nullable=False
    )
    id_sede = db.Column(db.String(100), db.ForeignKey("sedes.id_sede"), nullable=False)

    # Nullable: se llena cuando el lote viene de recibir una orden a
    # proveedor (le da trazabilidad a qué línea de orden lo generó)
    id_detalle_orden = db.Column(
        db.String(100),
        db.ForeignKey("detalle_orden_pedido_proveedor.id_detalle_orden"),
        nullable=True,
    )

    fecha_ingreso = db.Column(db.Date, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)

    cantidad_inicial = db.Column(db.Integer, nullable=False)
    cantidad_actual = db.Column(db.Integer, nullable=False)

    # OJO: NO se define aquí una relación hacia Producto porque
    # Producto.lotes ya está declarado con backref="producto" en producto.py
    # (definirla en ambos lados duplicaría el mapeo y SQLAlchemy reclamaría).

    def to_dict(self):
        return {
            "id_lote": self.id_lote,
            "id_producto": self.id_producto,
            "id_proveedor": self.id_proveedor,
            "id_sede": self.id_sede,
            "id_detalle_orden": self.id_detalle_orden,
            "fecha_ingreso": self.fecha_ingreso.isoformat(),
            "fecha_vencimiento": self.fecha_vencimiento.isoformat(),
            "cantidad_inicial": self.cantidad_inicial,
            "cantidad_actual": self.cantidad_actual,
        }
