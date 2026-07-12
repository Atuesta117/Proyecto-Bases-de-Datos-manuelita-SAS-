from app import db


class Producto(db.Model):
    __tablename__ = "productos"

    id_producto = db.Column(db.String(100), primary_key=True)
    id_proveedor = db.Column(
        db.String(100), db.ForeignKey("proveedores.id_proveedor"), nullable=False
    )
    id_tipo_iva = db.Column(
        db.String(100), db.ForeignKey("tipos_iva.id_tipo_iva"), nullable=False
    )
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.BigInteger, nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    peso = db.Column(db.Numeric(10, 3), nullable=False)
    unidad_medida = db.Column(db.String(10))  # g, kg, l, ml, galon
    activo = db.Column(db.Boolean, nullable=False, default=True)  # Eliminación lógica

    # Relaciones básicas para cargar inventario y lotes de forma sencilla
    stock = db.relationship(
        "StockProducto", backref="producto", uselist=False, cascade="all, delete-orphan"
    )
    lotes = db.relationship("Lote", backref="producto", lazy=True)

    # Necesaria para poder leer tiempo_entrega_promedio del proveedor sin
    # hacer una consulta aparte cada vez (dato pedido por el documento)
    proveedor = db.relationship("Proveedor", backref="productos", lazy=True)

    # Necesaria para poder leer el % de IVA al facturar sin consulta aparte
    tipo_iva = db.relationship("TipoIva", backref="productos", lazy=True)

    def to_dict_completo(self):
        """Devuelve toda la información calculada al vuelo para el frontend"""
        # Valores de inventario por defecto por si no tiene registro en STOCKPRODUCTOS
        inventario_actual = self.stock.cantidad_disponible if self.stock else 0
        demanda_diaria = (
            float(self.stock.demanda_diaria)
            if (self.stock and self.stock.demanda_diaria)
            else 0.0
        )
        stock_minimo = self.stock.stock_minimo if self.stock else 0

        # Cálculo dinámico de Días de Stock (NUNCA se guarda en BD, solo se calcula al vuelo)
        if demanda_diaria > 0:
            dias_stock = round(inventario_actual / demanda_diaria, 1)
        else:
            dias_stock = (
                999 if inventario_actual > 0 else 0
            )  # Evitamos división por cero

        # Clasificación de Estado según las reglas exactas de la guía
        if inventario_actual == 0 or dias_stock == 0:
            estado = "AGOTADO"
            accion = "Pedido Inmediato"
        elif dias_stock < 5:
            estado = "CRÍTICO"
            accion = "Pedido de Emergencia"
        elif 5 <= dias_stock <= 15:
            estado = "ALERTA"
            accion = "Realizar Pedido Normal"
        else:
            estado = "SEGURO"
            accion = "Mantener Monitoreo"

        # --- Dato recomendado por la guía: tiempo de entrega del proveedor ---
        tiempo_entrega_promedio = (
            self.proveedor.tiempo_entrega_promedio if self.proveedor else None
        )

        # Con el lead time del proveedor podemos calcular el "punto de reorden":
        # cuántas unidades necesitas para aguantar mientras llega el próximo pedido.
        punto_reorden = None
        necesita_pedido_por_tiempo_entrega = False
        if tiempo_entrega_promedio is not None and demanda_diaria > 0:
            punto_reorden = round(demanda_diaria * tiempo_entrega_promedio, 1)
            # Si lo que te queda de inventario (en días) es menor o igual a lo que
            # tarda en llegar un nuevo pedido, ya deberías haber pedido.
            necesita_pedido_por_tiempo_entrega = dias_stock <= tiempo_entrega_promedio

        return {
            "id_producto": self.id_producto,
            "id_proveedor": self.id_proveedor,
            "id_tipo_iva": self.id_tipo_iva,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "categoria": self.categoria,
            "peso": float(self.peso),
            "unidad_medida": self.unidad_medida,
            "activo": self.activo,
            # Campos de Stock agregados
            "inventario_actual": inventario_actual,
            "cantidad_reservada": self.stock.cantidad_reservada if self.stock else 0,
            "stock_minimo": stock_minimo,
            "demanda_diaria": demanda_diaria,
            # Campos calculados dinámicamente (nunca almacenados)
            "dias_stock": dias_stock,
            "estado_inventario": estado,
            "accion_recomendada": accion,
            "alerta_reabastecimiento": inventario_actual <= stock_minimo,
            # Campos derivados del proveedor (recomendación de la guía)
            "tiempo_entrega_promedio": tiempo_entrega_promedio,
            "punto_reorden": punto_reorden,
            "necesita_pedido_por_tiempo_entrega": necesita_pedido_por_tiempo_entrega,
        }
