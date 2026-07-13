from app import db
from datetime import datetime, date


class Factura(db.Model):
    __tablename__ = "facturas"

    id_factura = db.Column(db.String(100), primary_key=True)
    id_empresa = db.Column(
        db.String(100), db.ForeignKey("empresa.id_empresa"), nullable=False
    )
    id_cliente = db.Column(
        db.String(100), db.ForeignKey("clientes.id_cliente"), nullable=False
    )

    numero_factura = db.Column(db.String(50), unique=True, nullable=False)
    prefijo = db.Column(db.String(10))
    vigencia_resolucion = db.Column(db.String(100))
    fecha_generacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_expedicion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # CHECK real: 'efectivo','tarjeta','transferencia','contraentrega'
    metodo_pago = db.Column(db.String(20))
    # CHECK real: 'pendiente','confirmado','anulada'
    estado = db.Column(db.String(20))

    subtotal = db.Column(db.BigInteger, nullable=False)
    valor_iva = db.Column(db.BigInteger, nullable=False)
    total_pagar = db.Column(db.BigInteger, nullable=False)
    cufe = db.Column(db.String(150))
    codigo_qr = db.Column(db.Text)

    detalles = db.relationship(
        "DetalleFactura", backref="factura", cascade="all, delete-orphan", lazy=True
    )

    def to_dict(self):
        return {
            "id_factura": self.id_factura,
            "id_empresa": self.id_empresa,
            "id_cliente": self.id_cliente,
            "numero_factura": self.numero_factura,
            "prefijo": self.prefijo,
            "fecha_generacion": self.fecha_generacion.isoformat(),
            "fecha_expedicion": self.fecha_expedicion.isoformat(),
            "metodo_pago": self.metodo_pago,
            "estado": self.estado,
            "subtotal": self.subtotal,
            "valor_iva": self.valor_iva,
            "total_pagar": self.total_pagar,
            "cufe": self.cufe,
            "detalles": [d.to_dict() for d in self.detalles],
        }


class DetalleFactura(db.Model):
    __tablename__ = "detalle_factura"

    id_detalle = db.Column(db.String(100), primary_key=True)
    id_factura = db.Column(
        db.String(100), db.ForeignKey("facturas.id_factura"), nullable=False
    )
    id_producto = db.Column(
        db.String(100), db.ForeignKey("productos.id_producto"), nullable=False
    )

    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.BigInteger, nullable=False)
    porcentaje_iva = db.Column(db.Numeric(5, 2), nullable=False)
    valor_iva = db.Column(db.BigInteger, nullable=False)
    subtotal_item = db.Column(db.BigInteger, nullable=False)
    total_item = db.Column(db.BigInteger, nullable=False)

    def to_dict(self):
        return {
            "id_detalle": self.id_detalle,
            "id_factura": self.id_factura,
            "id_producto": self.id_producto,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "porcentaje_iva": float(self.porcentaje_iva),
            "valor_iva": self.valor_iva,
            "subtotal_item": self.subtotal_item,
            "total_item": self.total_item,
        }


class PedidoConfirmado(db.Model):
    __tablename__ = "pedido_confirmado"

    id_confirmacion = db.Column(db.String(100), primary_key=True)
    id_verificacion = db.Column(
        db.String(100),
        db.ForeignKey("verificar_pedido.id_verificacion"),
        unique=True,
        nullable=False,
    )
    id_factura = db.Column(
        db.String(100),
        db.ForeignKey("facturas.id_factura"),
        unique=True,
        nullable=False,
    )
    fecha_confirmacion = db.Column(db.Date, nullable=False, default=date.today)

    # Igual que en VerificarPedido: la columna real en BD es "esvalido"
    es_valido = db.Column("esvalido", db.Boolean, nullable=False, default=True)

    def to_dict(self):
        return {
            "id_confirmacion": self.id_confirmacion,
            "id_verificacion": self.id_verificacion,
            "id_factura": self.id_factura,
            "fecha_confirmacion": self.fecha_confirmacion.isoformat(),
            "es_valido": self.es_valido,
        }
