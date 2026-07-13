from app import db
from datetime import date


class Camion(db.Model):
    __tablename__ = "camion"

    id_camion = db.Column(db.String(100), primary_key=True)
    placa = db.Column(db.String(20), unique=True, nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    capacidad_kg = db.Column(db.Numeric(10, 3), nullable=False)

    # CHECK real: 'disponible','en_ruta','mantenimiento','fuera_de_servicio'
    estado = db.Column(db.String(20), nullable=False, default="disponible")
    kilometraje = db.Column(db.Integer, nullable=False, default=0)

    # Agregado en la migración: a qué sede pertenece el camión
    id_sede = db.Column(db.String(100), db.ForeignKey("sedes.id_sede"), nullable=True)

    def to_dict(self):
        return {
            "id_camion": self.id_camion,
            "placa": self.placa,
            "marca": self.marca,
            "modelo": self.modelo,
            "capacidad_kg": float(self.capacidad_kg),
            "estado": self.estado,
            "kilometraje": self.kilometraje,
            "id_sede": self.id_sede,
        }


class Conductor(db.Model):
    __tablename__ = "conductor"

    id_conductor = db.Column(db.String(100), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    licencia = db.Column(db.String(50), unique=True, nullable=False)
    fecha_vencimiento_licencia = db.Column(db.Date, nullable=False)

    # Agregados en la migración
    id_sede = db.Column(db.String(100), db.ForeignKey("sedes.id_sede"), nullable=True)
    disponible = db.Column(db.Boolean, nullable=False, default=True)

    def to_dict(self):
        return {
            "id_conductor": self.id_conductor,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "cedula": self.cedula,
            "telefono": self.telefono,
            "licencia": self.licencia,
            "fecha_vencimiento_licencia": self.fecha_vencimiento_licencia.isoformat(),
            "id_sede": self.id_sede,
            "disponible": self.disponible,
        }


class CamionConductor(db.Model):
    """Historial de qué conductor maneja qué camión (rango de fechas)."""

    __tablename__ = "camion_conductor"

    id_camion_conductor = db.Column(db.String(100), primary_key=True)
    id_camion = db.Column(
        db.String(100), db.ForeignKey("camion.id_camion"), nullable=False
    )
    id_conductor = db.Column(
        db.String(100), db.ForeignKey("conductor.id_conductor"), nullable=False
    )
    fecha_inicio = db.Column(db.Date, nullable=False, default=date.today)
    fecha_fin = db.Column(db.Date, nullable=True)  # NULL = asignación activa

    def to_dict(self):
        return {
            "id_camion_conductor": self.id_camion_conductor,
            "id_camion": self.id_camion,
            "id_conductor": self.id_conductor,
            "fecha_inicio": self.fecha_inicio.isoformat(),
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
        }


class Envio(db.Model):
    __tablename__ = "envios"

    id_envio = db.Column(db.String(100), primary_key=True)
    id_pedido_confirmado = db.Column(
        db.String(100),
        db.ForeignKey("pedido_confirmado.id_confirmacion"),
        unique=True,
        nullable=False,
    )

    # Agregado en la migración: sede física desde donde se despacha
    id_sede_origen = db.Column(
        db.String(100), db.ForeignKey("sedes.id_sede"), nullable=True
    )

    direccion_origen = db.Column(db.String(255), nullable=False)
    direccion_destino = db.Column(db.String(255), nullable=False)
    fecha_envio = db.Column(db.Date, nullable=False, default=date.today)
    fecha_entrega_estimada = db.Column(db.Date, nullable=False)

    # CHECK real: 'preparando','en_camino','entregado','devuelto'
    estado_envio = db.Column(db.String(20), nullable=False, default="preparando")
    # CHECK real: 'nacional','internacional'
    tipo_envio = db.Column(db.String(20), nullable=False)

    asignaciones = db.relationship(
        "AsignacionCamiones", backref="envio", cascade="all, delete-orphan", lazy=True
    )

    def to_dict(self):
        return {
            "id_envio": self.id_envio,
            "id_pedido_confirmado": self.id_pedido_confirmado,
            "id_sede_origen": self.id_sede_origen,
            "direccion_origen": self.direccion_origen,
            "direccion_destino": self.direccion_destino,
            "fecha_envio": self.fecha_envio.isoformat(),
            "fecha_entrega_estimada": self.fecha_entrega_estimada.isoformat(),
            "estado_envio": self.estado_envio,
            "tipo_envio": self.tipo_envio,
            "camiones_asignados": [a.id_camion for a in self.asignaciones],
        }


class EnvioNacional(db.Model):
    __tablename__ = "envio_nacional"

    id_envio = db.Column(
        db.String(100), db.ForeignKey("envios.id_envio"), primary_key=True
    )
    departamento = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    codigo_postal = db.Column(db.String(10), nullable=False)
    transportadora_local = db.Column(db.String(150), nullable=False)

    def to_dict(self):
        return {
            "id_envio": self.id_envio,
            "departamento": self.departamento,
            "ciudad": self.ciudad,
            "codigo_postal": self.codigo_postal,
            "transportadora_local": self.transportadora_local,
        }


class EnvioInternacional(db.Model):
    __tablename__ = "envio_internacional"

    id_envio = db.Column(
        db.String(100), db.ForeignKey("envios.id_envio"), primary_key=True
    )
    pais_destino = db.Column(db.String(100), nullable=False)
    aduana = db.Column(db.String(150))
    numero_tracking_internacional = db.Column(
        db.String(100), unique=True, nullable=False
    )
    costo_aduana = db.Column(db.Numeric(20, 2), nullable=False)
    divisa = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            "id_envio": self.id_envio,
            "pais_destino": self.pais_destino,
            "aduana": self.aduana,
            "numero_tracking_internacional": self.numero_tracking_internacional,
            "costo_aduana": float(self.costo_aduana),
            "divisa": self.divisa,
        }


class AsignacionCamiones(db.Model):
    __tablename__ = "asignacion_camiones"

    id_envio_camion_nor = db.Column(db.String(100), primary_key=True)
    id_envio = db.Column(
        db.String(100), db.ForeignKey("envios.id_envio"), nullable=False
    )
    id_camion = db.Column(
        db.String(100), db.ForeignKey("camion.id_camion"), nullable=False
    )
    fecha_carga = db.Column(db.Date, nullable=False, default=date.today)
