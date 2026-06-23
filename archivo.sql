

-- 1. Tabla USUARIOS
CREATE TABLE USUARIOS (
   id_usuario VARCHAR(100) PRIMARY KEY,
   nombre VARCHAR(100) NOT NULL,
   apellido VARCHAR(100) NOT NULL,
   email VARCHAR(150) NOT NULL UNIQUE,
   contrasena VARCHAR(255) NOT NULL,
   telefono VARCHAR(20),
   direccion VARCHAR(255),
   tipo_usuario VARCHAR(20) NOT NULL CHECK (tipo_usuario IN ('admin', 'cliente')),
   fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE
);

-- 2. Tabla PROVEEDOR
CREATE TABLE PROVEEDOR (
   id_proveedor VARCHAR(100) PRIMARY KEY,
   nombre_empresa VARCHAR(150) NOT NULL,
   nit VARCHAR(20) NOT NULL UNIQUE,
   contacto VARCHAR(100),
   telefono VARCHAR(20),
   email VARCHAR(150) NOT NULL UNIQUE,
   direccion VARCHAR(255)
);

-- 3. Tabla LOTES
CREATE TABLE LOTES (
   id_lote VARCHAR(100) PRIMARY KEY,
   id_proveedor VARCHAR(100) NOT NULL REFERENCES PROVEEDOR(id_proveedor) ON DELETE RESTRICT,
   fecha_ingreso DATE NOT NULL,
   fecha_vencimiento DATE NOT NULL,
   cantidad_inicial INTEGER NOT NULL CHECK (cantidad_inicial > 0),
   cantidad_actual INTEGER NOT NULL CHECK (cantidad_actual >= 0),
   CONSTRAINT chk_fechas_lote CHECK (fecha_vencimiento > fecha_ingreso),
   CONSTRAINT chk_cantidades CHECK (cantidad_actual <= cantidad_inicial)
);

-- 4. Tabla PRODUCTO
CREATE TABLE PRODUCTO (
   id_producto VARCHAR(100) PRIMARY KEY,
   id_lote VARCHAR(100) NOT NULL REFERENCES LOTES(id_lote) ON DELETE RESTRICT,
   nombre VARCHAR(150) NOT NULL,
   descripcion TEXT,
   precio INTEGER NOT NULL CHECK (precio > 0),
   categoria VARCHAR(100) NOT NULL,
   peso NUMERIC(10, 3) NOT NULL CHECK (peso > 0),
   unidad_medida VARCHAR(10) NOT NULL CHECK (unidad_medida IN ('g', 'kg', 'l', 'ml', 'galon'))
);

-- 5. Tabla STOCKPRODUCTOS
CREATE TABLE STOCKPRODUCTOS (
   id_stock VARCHAR(100) PRIMARY KEY,
   id_producto VARCHAR(100) NOT NULL UNIQUE REFERENCES PRODUCTO(id_producto),
   cantidad_disponible INTEGER NOT NULL CHECK (cantidad_disponible >= 0),
   cantidad_reservada INTEGER NOT NULL CHECK (cantidad_reservada >= 0),
   stock_minimo INTEGER NOT NULL CHECK (stock_minimo >= 0),
   ultima_actualizacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT chk_reservada_no_supera_disponible CHECK (cantidad_reservada <= cantidad_disponible)
);

-- 6. Tabla PEDIDO
CREATE TABLE PEDIDO (
   id_pedido VARCHAR(100) PRIMARY KEY,
   id_usuario VARCHAR(100) NOT NULL REFERENCES USUARIOS(id_usuario) ON DELETE RESTRICT,
   fecha_pedido DATE NOT NULL DEFAULT CURRENT_DATE,
   estado VARCHAR(20) NOT NULL CHECK (estado IN ('pendiente', 'confirmado', 'enviado', 'entregado', 'cancelado')),
   metodo_pago VARCHAR(20) NOT NULL CHECK (metodo_pago IN ('efectivo', 'tarjeta', 'transferencia', 'contraentrega')),
   precio_pedido BIGINT NOT NULL CHECK (precio_pedido >= 0),
   precio_envio BIGINT NOT NULL CHECK (precio_envio >= 0)
);

-- 7. Tabla PRODUCTOS_ASOCIADOS
CREATE TABLE PRODUCTOS_ASOCIADOS (
   id_productos_asociados VARCHAR(100) PRIMARY KEY,
   id_pedido VARCHAR(100) NOT NULL REFERENCES PEDIDO(id_pedido),
   id_producto VARCHAR(100) NOT NULL REFERENCES PRODUCTO(id_producto) ON DELETE RESTRICT,
   cantidad INTEGER NOT NULL CHECK (cantidad > 0),
   CONSTRAINT uq_pedido_producto UNIQUE (id_pedido, id_producto)
);

-- 8. Tabla VERIFICAR_PEDIDO
CREATE TABLE VERIFICAR_PEDIDO (
   id_verificacion VARCHAR(100) PRIMARY KEY,
   id_pedido VARCHAR(100) NOT NULL UNIQUE REFERENCES PEDIDO(id_pedido),
   fecha_verificacion DATE NOT NULL DEFAULT CURRENT_DATE,
   stock_disponible INTEGER NOT NULL CHECK (stock_disponible >= 0),
   observaciones TEXT,
   esValido BOOLEAN NOT NULL
);

-- 9. Tabla PEDIDO_CONFIRMADO
CREATE TABLE PEDIDO_CONFIRMADO (
   id_confirmacion VARCHAR(100) PRIMARY KEY,
   id_verificacion VARCHAR(100) NOT NULL UNIQUE REFERENCES VERIFICAR_PEDIDO(id_verificacion) ON DELETE RESTRICT,
   fecha_confirmacion DATE NOT NULL DEFAULT CURRENT_DATE,
   numero_factura VARCHAR(50) NOT NULL UNIQUE,
   esValido BOOLEAN NOT NULL CHECK (esValido = TRUE)
);

-- 10. Tabla HISTORIAL_PEDIDOS
CREATE TABLE HISTORIAL_PEDIDOS (
   id_historial VARCHAR(100) PRIMARY KEY,
   id_usuario VARCHAR(100) NOT NULL REFERENCES USUARIOS(id_usuario) ON DELETE RESTRICT,
   estado_anterior VARCHAR(20) NOT NULL CHECK (estado_anterior IN ('pendiente', 'confirmado', 'enviado', 'entregado', 'cancelado')),
   estado_nuevo VARCHAR(20) NOT NULL CHECK (estado_nuevo IN ('pendiente', 'confirmado', 'enviado', 'entregado', 'cancelado')),
   fecha_cambio DATE NOT NULL DEFAULT CURRENT_DATE,
   CONSTRAINT chk_estados_distintos CHECK (estado_anterior <> estado_nuevo)
);

-- 11. Tabla HISTORIAL_PEDIDOS_NOR
CREATE TABLE HISTORIAL_PEDIDOS_NOR (
   id_historial_nor VARCHAR(100) PRIMARY KEY,
   id_pedido VARCHAR(100) NOT  NULL REFERENCES PEDIDO(id_pedido),
   id_historial VARCHAR(100) NOT  NULL REFERENCES HISTORIAL_PEDIDOS(id_historial) ON DELETE RESTRICT,
   CONSTRAINT uq_pedido_historial UNIQUE (id_pedido, id_historial)
);

-- 12. Tabla CAMION
CREATE TABLE CAMION (
   id_camion VARCHAR(100) PRIMARY KEY,
   placa VARCHAR(20) NOT NULL UNIQUE,
   marca VARCHAR(100) NOT NULL,
   modelo VARCHAR(100) NOT NULL,
   capacidad_kg NUMERIC(10, 3) NOT NULL CHECK (capacidad_kg > 0),
   estado VARCHAR(20) NOT NULL CHECK (estado IN ('disponible', 'en_ruta', 'mantenimiento', 'fuera_de_servicio')),
   kilometraje INTEGER NOT NULL CHECK (kilometraje >= 0)
);

-- 13. Tabla CONDUCTOR
CREATE TABLE CONDUCTOR (
   id_conductor VARCHAR(100) PRIMARY KEY,
   nombre VARCHAR(100) NOT NULL,
   apellido VARCHAR(100) NOT NULL,
   cedula VARCHAR(20) NOT NULL UNIQUE,
   telefono VARCHAR(20) NOT NULL,
   licencia VARCHAR(50) NOT NULL UNIQUE,
   fecha_vencimiento_licencia DATE NOT NULL
);

-- 14. Tabla CAMION_CONDUCTOR
CREATE TABLE CAMION_CONDUCTOR (
   id_camion_conductor VARCHAR(100) PRIMARY KEY,
   id_camion VARCHAR(100) NOT NULL REFERENCES CAMION(id_camion),
   id_conductor VARCHAR(100) NOT NULL REFERENCES CONDUCTOR(id_conductor),
   fecha_inicio DATE NOT NULL,
   fecha_fin DATE,
   CONSTRAINT uq_camion_conductor UNIQUE (id_camion, id_conductor),
   CONSTRAINT chk_fechas_conductor CHECK (fecha_fin IS NULL OR fecha_fin > fecha_inicio)
);

-- 15. Tabla ENVIOS
CREATE TABLE ENVIOS (
   id_envio VARCHAR(100) PRIMARY KEY,
   id_pedido_confirmado VARCHAR(100) NOT NULL UNIQUE REFERENCES PEDIDO_CONFIRMADO(id_confirmacion) ON DELETE RESTRICT,
   direccion_origen VARCHAR(255) NOT NULL,
   direccion_destino VARCHAR(255) NOT NULL,
   fecha_envio DATE NOT NULL DEFAULT CURRENT_DATE,
   fecha_entrega_estimada DATE NOT NULL,
   estado_envio VARCHAR(20) NOT NULL CHECK (estado_envio IN ('preparando', 'en_camino', 'entregado', 'devuelto')),
   tipo_envio VARCHAR(20) NOT NULL CHECK (tipo_envio IN ('nacional', 'internacional')),
   CONSTRAINT chk_fechas_envio CHECK (fecha_entrega_estimada >= fecha_envio)
);

-- 16. Tabla ENVIO_NACIONAL
CREATE TABLE ENVIO_NACIONAL (
   id_envio VARCHAR(100) PRIMARY KEY REFERENCES ENVIOS(id_envio),
   departamento VARCHAR(100) NOT NULL,
   ciudad VARCHAR(100) NOT NULL,
   codigo_postal VARCHAR(10) NOT NULL,
   transportadora_local VARCHAR(150) NOT NULL
);

-- 17. Tabla ENVIO_INTERNACIONAL
CREATE TABLE ENVIO_INTERNACIONAL (
   id_envio VARCHAR(100) PRIMARY KEY REFERENCES ENVIOS(id_envio),
   pais_destino VARCHAR(100) NOT NULL,
   aduana VARCHAR(150),
   numero_tracking_internacional VARCHAR(100) NOT NULL UNIQUE,
   costo_aduana NUMERIC(20, 2) NOT NULL CHECK (costo_aduana >= 0),
   divisa VARCHAR(10) NOT NULL
);

-- 18. Tabla ASIGNACION_CAMIONES
CREATE TABLE ASIGNACION_CAMIONES (
   id_envio_camion_nor VARCHAR(100) PRIMARY KEY,
   id_envio VARCHAR(100) NOT NULL UNIQUE REFERENCES ENVIOS(id_envio),
   id_camion VARCHAR(100) NOT NULL REFERENCES CAMION(id_camion) ON DELETE RESTRICT,
   fecha_carga DATE NOT NULL DEFAULT CURRENT_DATE
);

