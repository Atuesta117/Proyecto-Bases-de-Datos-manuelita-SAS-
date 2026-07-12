
-- CLIENTES
CREATE TABLE CLIENTES (
    id_cliente             VARCHAR(100) PRIMARY KEY,
    nombre_razon_social    VARCHAR(100) NOT NULL,
    tipo_documento         VARCHAR(5)   NOT NULL CHECK (tipo_documento IN ('CC','NIT','CE')),
    numero_identificacion  VARCHAR(20)  NOT NULL UNIQUE,
    habeas_data            BOOLEAN      NOT NULL DEFAULT FALSE,
    ciudad                 VARCHAR(100) NOT NULL DEFAULT 'Cali',
    direccion_operativa    VARCHAR(255),
    direccion_residencia   VARCHAR(255),
    email                  VARCHAR(150) NOT NULL UNIQUE,
    num_contacto           VARCHAR(20),
    tipo_num_contacto      VARCHAR(20)  CHECK (tipo_num_contacto IN ('celular','telefono')),
    representante_legal    VARCHAR(150),
    tipo_regimen           VARCHAR(25)  NOT NULL DEFAULT 'no_responsable_iva'
                               CHECK (tipo_regimen IN ('responsable_iva','no_responsable_iva')),
    fecha_registro         DATE         NOT NULL DEFAULT CURRENT_DATE
);

-- PROVEEDORES
 CREATE TABLE PROVEEDORES (
    id_proveedor            VARCHAR(100) PRIMARY KEY,
    nombre_razon_social     VARCHAR(100) NOT NULL,
    tipo_documento          VARCHAR(5)   NOT NULL CHECK (tipo_documento IN ('CC','NIT','CE')),
    numero_identificacion   VARCHAR(20)  NOT NULL UNIQUE,
    habeas_data             BOOLEAN      NOT NULL DEFAULT FALSE,
    ciudad                  VARCHAR(100) NOT NULL DEFAULT 'Cali',
    direccion_operativa     VARCHAR(255),
    direccion_residencia    VARCHAR(255),
    email                   VARCHAR(150) NOT NULL UNIQUE,
    num_contacto            VARCHAR(20),
    tipo_num_contacto       VARCHAR(20)  CHECK (tipo_num_contacto IN ('celular','telefono')),
    representante_legal     VARCHAR(150),
    tipo_regimen            VARCHAR(25)  NOT NULL DEFAULT 'no_responsable_iva'
                                CHECK (tipo_regimen IN ('responsable_iva','no_responsable_iva')),
    fecha_registro          DATE         NOT NULL DEFAULT CURRENT_DATE,
    rut                     VARCHAR(20)  NOT NULL UNIQUE,
    banco                   VARCHAR(100),
    tipo_cuenta             VARCHAR(20)  CHECK (tipo_cuenta IN ('ahorros','corriente')),
    numero_cuenta           VARCHAR(30),
    tipo_proveedor          VARCHAR(100) NOT NULL DEFAULT 'materia_prima',
    tiempo_entrega_promedio INTEGER      NOT NULL DEFAULT 0 CHECK (tiempo_entrega_promedio >= 0),
    contacto_comercial      VARCHAR(100),
    contacto_cartera        VARCHAR(100),
    contacto_logistico      VARCHAR(100),
    condiciones_pago        INTEGER      NOT NULL DEFAULT 30 CHECK (condiciones_pago >= 0),
    calificacion            SMALLINT     NOT NULL DEFAULT 3 CHECK (calificacion BETWEEN 1 AND 5)
);

-- TIPOS_IVA
CREATE TABLE TIPOS_IVA (
    id_tipo_iva  VARCHAR(100) PRIMARY KEY,
    nombre       VARCHAR(50) NOT NULL UNIQUE,
    porcentaje   NUMERIC(5,2) NOT NULL CHECK (porcentaje >= 0)
);

-- PRODUCTOS
CREATE TABLE PRODUCTOS (
    id_producto     VARCHAR(100) PRIMARY KEY,

    id_proveedor    VARCHAR(100) NOT NULL
        REFERENCES PROVEEDORES(id_proveedor)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    id_tipo_iva     VARCHAR(100) NOT NULL
        REFERENCES TIPOS_IVA(id_tipo_iva)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    nombre          VARCHAR(150) NOT NULL,
    descripcion     TEXT,
    precio          BIGINT NOT NULL CHECK (precio > 0),
    categoria       VARCHAR(100) NOT NULL,
    peso            NUMERIC(10,3) NOT NULL CHECK (peso > 0),
    unidad_medida   VARCHAR(10) CHECK (unidad_medida IN ('g','kg','l','ml','galon')),
    activo          BOOLEAN NOT NULL DEFAULT TRUE  -- eliminación lógica (recomendada en la guía)
);

-- EMPRESA
CREATE TABLE EMPRESA (
    id_empresa           VARCHAR(100) PRIMARY KEY,
    nit                  VARCHAR(20)  NOT NULL UNIQUE,
    razon_social         VARCHAR(150) NOT NULL,
    nombre_comercial     VARCHAR(150),
    direccion            VARCHAR(255) NOT NULL,
    ciudad               VARCHAR(100) NOT NULL DEFAULT 'Cali',
    telefono             VARCHAR(20),
    email                VARCHAR(150),
    representante_legal  VARCHAR(150),
    tipo_regimen         VARCHAR(25) NOT NULL DEFAULT 'responsable_iva'
                             CHECK (tipo_regimen IN ('responsable_iva','no_responsable_iva'))
);

-- SEDES
CREATE TABLE SEDES (
    id_sede         VARCHAR(100) PRIMARY KEY,

    id_empresa      VARCHAR(100) NOT NULL
        REFERENCES EMPRESA(id_empresa)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    nombre_sede     VARCHAR(100) NOT NULL,
    tipo_sede       VARCHAR(30)  NOT NULL DEFAULT 'bodega'
                        CHECK (tipo_sede IN ('bodega','planta','punto_venta','administrativa')),
    ciudad          VARCHAR(100) NOT NULL,
    direccion       VARCHAR(255) NOT NULL,
    telefono        VARCHAR(20),
    es_principal    BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_apertura  DATE NOT NULL DEFAULT CURRENT_DATE
);

-- ORDENES_PEDIDO_PROVEEDOR
CREATE TABLE ORDENES_PEDIDO_PROVEEDOR (
    id_orden        VARCHAR(100) PRIMARY KEY,
    numero_orden    BIGSERIAL UNIQUE,           -- consecutivo interno (1,2,3...)

    id_sede         VARCHAR(100) NOT NULL
        REFERENCES SEDES(id_sede)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    id_proveedor    VARCHAR(100) NOT NULL
        REFERENCES PROVEEDORES(id_proveedor)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    fecha_pedido    DATE NOT NULL DEFAULT CURRENT_DATE,
    lugar_entrega   VARCHAR(255) NOT NULL,
    estado          VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                        CHECK (estado IN ('pendiente','en_transito','recibido','cancelado'))
);

-- DETALLE_ORDEN_PEDIDO_PROVEEDOR
CREATE TABLE DETALLE_ORDEN_PEDIDO_PROVEEDOR (
    id_detalle_orden  VARCHAR(100) PRIMARY KEY,

    id_orden          VARCHAR(100) NOT NULL
        REFERENCES ORDENES_PEDIDO_PROVEEDOR(id_orden)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    id_producto       VARCHAR(100) NOT NULL
        REFERENCES PRODUCTOS(id_producto)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    cantidad          INTEGER NOT NULL CHECK (cantidad > 0),
    costo_unitario    BIGINT  NOT NULL CHECK (costo_unitario >= 0),
    CONSTRAINT uq_orden_producto UNIQUE (id_orden, id_producto)
);

-- LOTES
CREATE TABLE LOTES (
    id_lote             VARCHAR(100) PRIMARY KEY,

    id_producto         VARCHAR(100) NOT NULL
        REFERENCES PRODUCTOS(id_producto)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    id_proveedor        VARCHAR(100) NOT NULL
        REFERENCES PROVEEDORES(id_proveedor)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    id_sede             VARCHAR(100) NOT NULL
        REFERENCES SEDES(id_sede)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    id_detalle_orden    VARCHAR(100)
        REFERENCES DETALLE_ORDEN_PEDIDO_PROVEEDOR(id_detalle_orden)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    fecha_ingreso       DATE    NOT NULL,
    fecha_vencimiento   DATE    NOT NULL,
    cantidad_inicial    INTEGER NOT NULL CHECK (cantidad_inicial > 0),
    cantidad_actual     INTEGER NOT NULL CHECK (cantidad_actual >= 0),

    CONSTRAINT chk_fechas_lote CHECK (fecha_vencimiento > fecha_ingreso),
    CONSTRAINT chk_cantidades  CHECK (cantidad_actual <= cantidad_inicial)
);

-- STOCKPRODUCTOS
CREATE TABLE STOCKPRODUCTOS (
    id_stock              VARCHAR(100) PRIMARY KEY,

    id_producto           VARCHAR(100) NOT NULL UNIQUE
        REFERENCES PRODUCTOS(id_producto)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    cantidad_disponible   INTEGER NOT NULL CHECK (cantidad_disponible >= 0),
    cantidad_reservada    INTEGER NOT NULL CHECK (cantidad_reservada >= 0),
    stock_minimo          INTEGER NOT NULL CHECK (stock_minimo >= 0),
    demanda_diaria        NUMERIC(10,3) NOT NULL DEFAULT 0 CHECK (demanda_diaria >= 0),
    ultima_actualizacion  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_reservada_no_supera_disponible CHECK (cantidad_reservada <= cantidad_disponible)
);

-- PEDIDO
CREATE TABLE PEDIDO (
    id_pedido       VARCHAR(100) PRIMARY KEY,

    id_cliente      VARCHAR(100) NOT NULL
        REFERENCES CLIENTES(id_cliente)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    fecha_pedido    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado          VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                        CHECK (estado IN ('pendiente','verificado','confirmado','rechazado','anulado')),
    observaciones   TEXT
);

-- DETALLE_PEDIDO
CREATE TABLE DETALLE_PEDIDO (
    id_detalle_pedido   VARCHAR(100) PRIMARY KEY,

    id_pedido           VARCHAR(100) NOT NULL
        REFERENCES PEDIDO(id_pedido)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    id_producto         VARCHAR(100) NOT NULL
        REFERENCES PRODUCTOS(id_producto)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    cantidad_solicitada INTEGER NOT NULL CHECK (cantidad_solicitada > 0),
    CONSTRAINT uq_pedido_producto UNIQUE (id_pedido, id_producto)
);

-- VERIFICAR_PEDIDO
CREATE TABLE VERIFICAR_PEDIDO (
    id_verificacion     VARCHAR(100) PRIMARY KEY,

    id_pedido           VARCHAR(100) NOT NULL UNIQUE
        REFERENCES PEDIDO(id_pedido)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    fecha_verificacion  DATE NOT NULL DEFAULT CURRENT_DATE,
    esValido            BOOLEAN NOT NULL,
    observaciones       TEXT
);

-- DETALLE_PEDIDO_LOTE
CREATE TABLE DETALLE_PEDIDO_LOTE (
    id_asignacion       VARCHAR(100) PRIMARY KEY,

    id_detalle_pedido   VARCHAR(100) NOT NULL
        REFERENCES DETALLE_PEDIDO(id_detalle_pedido)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    id_lote             VARCHAR(100) NOT NULL
        REFERENCES LOTES(id_lote)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    cantidad_asignada   INTEGER NOT NULL CHECK (cantidad_asignada > 0),
    CONSTRAINT uq_detalle_lote UNIQUE (id_detalle_pedido, id_lote)
);

-- FACTURAS
CREATE TABLE FACTURAS (
    id_factura          VARCHAR(100) PRIMARY KEY,

    id_empresa          VARCHAR(100) NOT NULL
        REFERENCES EMPRESA(id_empresa)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    id_cliente          VARCHAR(100) NOT NULL
        REFERENCES CLIENTES(id_cliente)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    numero_factura      VARCHAR(50) UNIQUE NOT NULL,
    prefijo             VARCHAR(10),
    vigencia_resolucion VARCHAR(100),
    fecha_generacion    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expedicion    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    metodo_pago         VARCHAR(20)
        CHECK (metodo_pago IN ('efectivo','tarjeta','transferencia','contraentrega')),

    estado              VARCHAR(20)
        CHECK (estado IN ('pendiente','confirmado','anulada')),

    subtotal            BIGINT NOT NULL CHECK (subtotal >= 0),
    valor_iva           BIGINT NOT NULL CHECK (valor_iva >= 0),
    total_pagar         BIGINT NOT NULL CHECK (total_pagar >= 0),
    cufe                VARCHAR(150),
    codigo_qr           TEXT
);

-- DETALLE_FACTURA
CREATE TABLE DETALLE_FACTURA (
    id_detalle          VARCHAR(100) PRIMARY KEY,

    id_factura          VARCHAR(100) NOT NULL
        REFERENCES FACTURAS(id_factura)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    id_producto         VARCHAR(100) NOT NULL
        REFERENCES PRODUCTOS(id_producto)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    cantidad            INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario     BIGINT NOT NULL CHECK (precio_unitario >= 0),
    porcentaje_iva      NUMERIC(5,2) NOT NULL CHECK (porcentaje_iva >= 0),
    valor_iva           BIGINT NOT NULL CHECK (valor_iva >= 0),
    subtotal_item       BIGINT NOT NULL CHECK (subtotal_item >= 0),
    total_item          BIGINT NOT NULL CHECK (total_item >= 0)
);

-- PEDIDO_CONFIRMADO
CREATE TABLE PEDIDO_CONFIRMADO (
    id_confirmacion     VARCHAR(100) PRIMARY KEY,

    id_verificacion     VARCHAR(100) NOT NULL UNIQUE
        REFERENCES VERIFICAR_PEDIDO(id_verificacion)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    id_factura          VARCHAR(100) NOT NULL UNIQUE
        REFERENCES FACTURAS(id_factura)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    fecha_confirmacion  DATE NOT NULL DEFAULT CURRENT_DATE,
    esValido            BOOLEAN NOT NULL CHECK (esValido = TRUE)
);

-- CAMION
-- MODIFICADO: se agrega id_sede para saber a qué sede pertenece el camión
-- (necesario para poder filtrar "camiones disponibles en esta sede").
CREATE TABLE CAMION (
    id_camion       VARCHAR(100) PRIMARY KEY,

    id_sede         VARCHAR(100)
        REFERENCES SEDES(id_sede)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    placa           VARCHAR(20)   NOT NULL UNIQUE,
    marca           VARCHAR(100)  NOT NULL,
    modelo          VARCHAR(100)  NOT NULL,
    capacidad_kg    NUMERIC(10,3) NOT NULL CHECK (capacidad_kg > 0),
    estado          VARCHAR(20)   NOT NULL
                        CHECK (estado IN ('disponible','en_ruta','mantenimiento','fuera_de_servicio')),
    kilometraje     INTEGER       NOT NULL CHECK (kilometraje >= 0)
);

-- CONDUCTOR
-- MODIFICADO: se agrega id_sede (a qué sede pertenece el conductor) y
-- disponible (si puede ser asignado a un nuevo envío ahora mismo).
CREATE TABLE CONDUCTOR (
    id_conductor                VARCHAR(100) PRIMARY KEY,

    id_sede                     VARCHAR(100)
        REFERENCES SEDES(id_sede)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    nombre                      VARCHAR(100) NOT NULL,
    apellido                    VARCHAR(100) NOT NULL,
    cedula                      VARCHAR(20)  NOT NULL UNIQUE,
    telefono                    VARCHAR(20)  NOT NULL,
    licencia                    VARCHAR(50)  NOT NULL UNIQUE,
    fecha_vencimiento_licencia  DATE         NOT NULL,
    disponible                  BOOLEAN      NOT NULL DEFAULT TRUE
);

-- CAMION_CONDUCTOR
CREATE TABLE CAMION_CONDUCTOR (
    id_camion_conductor  VARCHAR(100) PRIMARY KEY,

    id_camion            VARCHAR(100) NOT NULL
        REFERENCES CAMION(id_camion)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    id_conductor         VARCHAR(100) NOT NULL
        REFERENCES CONDUCTOR(id_conductor)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    fecha_inicio  DATE NOT NULL,
    fecha_fin     DATE,

    CONSTRAINT uq_camion_conductor  UNIQUE (id_camion, id_conductor, fecha_inicio),
    CONSTRAINT chk_fechas_conductor CHECK (fecha_fin IS NULL OR fecha_fin > fecha_inicio)
);

-- ENVIOS
-- MODIFICADO: se agrega id_sede_origen para saber desde qué sede/bodega
-- se despacha el envío (antes solo existía direccion_origen como texto
-- libre, sin relación real a una sede física).
CREATE TABLE ENVIOS (
    id_envio                VARCHAR(100) PRIMARY KEY,

    id_pedido_confirmado    VARCHAR(100) NOT NULL UNIQUE
        REFERENCES PEDIDO_CONFIRMADO(id_confirmacion)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    id_sede_origen          VARCHAR(100)
        REFERENCES SEDES(id_sede)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    direccion_origen        VARCHAR(255) NOT NULL,
    direccion_destino       VARCHAR(255) NOT NULL,
    fecha_envio             DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_entrega_estimada  DATE NOT NULL,
    estado_envio            VARCHAR(20) NOT NULL
                                CHECK (estado_envio IN ('preparando','en_camino','entregado','devuelto')),
    tipo_envio               VARCHAR(20) NOT NULL
                                CHECK (tipo_envio IN ('nacional','internacional')),

    CONSTRAINT chk_fechas_envio CHECK (fecha_entrega_estimada >= fecha_envio)
);

-- ENVIO_NACIONAL
CREATE TABLE ENVIO_NACIONAL (
    id_envio              VARCHAR(100) PRIMARY KEY
        REFERENCES ENVIOS(id_envio)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    departamento          VARCHAR(100) NOT NULL,
    ciudad                VARCHAR(100) NOT NULL,
    codigo_postal         VARCHAR(10)  NOT NULL,
    transportadora_local  VARCHAR(150) NOT NULL
);

-- ENVIO_INTERNACIONAL
CREATE TABLE ENVIO_INTERNACIONAL (
    id_envio                        VARCHAR(100) PRIMARY KEY
        REFERENCES ENVIOS(id_envio)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    pais_destino                    VARCHAR(100) NOT NULL,
    aduana                          VARCHAR(150),
    numero_tracking_internacional   VARCHAR(100) NOT NULL UNIQUE,
    costo_aduana                    NUMERIC(20,2) NOT NULL CHECK (costo_aduana >= 0),
    divisa                          VARCHAR(10) NOT NULL
);

-- ASIGNACION_CAMIONES
CREATE TABLE ASIGNACION_CAMIONES (
    id_envio_camion_nor  VARCHAR(100) PRIMARY KEY,

    id_envio             VARCHAR(100) NOT NULL
        REFERENCES ENVIOS(id_envio)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    id_camion            VARCHAR(100) NOT NULL
        REFERENCES CAMION(id_camion)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    fecha_carga          DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT uq_envio_camion UNIQUE (id_envio, id_camion)
);

-- Índices adicionales para las consultas de disponibilidad por sede
CREATE INDEX idx_camion_sede_estado ON CAMION (id_sede, estado);
CREATE INDEX idx_conductor_sede_disponible ON CONDUCTOR (id_sede, disponible);
