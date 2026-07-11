-- =====================================================================
-- MODIFICACIONES AL ESQUEMA - v2
-- Adapta el esquema original (pensado para logística) a los
-- requerimientos del Proyecto_BD_v1: Clientes, Proveedores, Productos
-- y Facturas.
--
-- IMPORTANTE: correr esto en pgAdmin sobre la BD que ya tiene el
-- esquema de archivo.sql cargado. Si alguna tabla ya tiene filas
-- cargadas, los ALTER TABLE ... ADD COLUMN ... NOT NULL sin DEFAULT
-- van a fallar. Como estamos en fase de diseño (sin datos aún),
-- deberían correr limpio. Si te falla, hace TRUNCATE TABLE antes.
-- =====================================================================


-- =====================================================================
-- 1. USUARIOS -> CLIENTES
-- =====================================================================
ALTER TABLE USUARIOS RENAME TO CLIENTES;

ALTER TABLE CLIENTES RENAME COLUMN id_usuario TO id_cliente;

-- Ya no necesitamos login: esta tabla ahora es "cliente del negocio",
-- no "usuario de la app"
ALTER TABLE CLIENTES DROP COLUMN contrasena;
ALTER TABLE CLIENTES DROP COLUMN tipo_usuario;

-- nombre + apellido -> un solo campo (para que sirva tanto para
-- persona natural como para razón social de empresa)
ALTER TABLE CLIENTES RENAME COLUMN nombre TO nombre_razon_social;
ALTER TABLE CLIENTES DROP COLUMN apellido;

ALTER TABLE CLIENTES ADD COLUMN tipo_documento VARCHAR(5) NOT NULL
    CHECK (tipo_documento IN ('CC','NIT','CE'));

ALTER TABLE CLIENTES ADD COLUMN numero_identificacion VARCHAR(20) NOT NULL UNIQUE;

ALTER TABLE CLIENTES ADD COLUMN habeas_data BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE CLIENTES ADD COLUMN ciudad VARCHAR(100) NOT NULL DEFAULT 'Cali';

-- la "direccion" original pasa a ser la de residencia, y agregamos
-- la operativa (para cuando el cliente es una empresa)
ALTER TABLE CLIENTES RENAME COLUMN direccion TO direccion_residencia;
ALTER TABLE CLIENTES ADD COLUMN direccion_operativa VARCHAR(255);

ALTER TABLE CLIENTES ADD COLUMN representante_legal VARCHAR(150);

ALTER TABLE CLIENTES ADD COLUMN tipo_regimen VARCHAR(25) NOT NULL
    DEFAULT 'no_responsable_iva'
    CHECK (tipo_regimen IN ('responsable_iva','no_responsable_iva'));


-- =====================================================================
-- 2. PROVEEDOR -> PROVEEDORES
-- =====================================================================
ALTER TABLE PROVEEDOR RENAME TO PROVEEDORES;

ALTER TABLE PROVEEDORES RENAME COLUMN nombre_empresa TO nombre_razon_social;
ALTER TABLE PROVEEDORES RENAME COLUMN nit TO rut;

ALTER TABLE PROVEEDORES ADD COLUMN tipo_documento VARCHAR(5) NOT NULL
    DEFAULT 'NIT' CHECK (tipo_documento IN ('NIT','CC','CE'));

ALTER TABLE PROVEEDORES ADD COLUMN banco VARCHAR(100);
ALTER TABLE PROVEEDORES ADD COLUMN tipo_cuenta VARCHAR(20)
    CHECK (tipo_cuenta IN ('ahorros','corriente'));
ALTER TABLE PROVEEDORES ADD COLUMN numero_cuenta VARCHAR(30);

ALTER TABLE PROVEEDORES ADD COLUMN tipo_proveedor VARCHAR(100) NOT NULL
    DEFAULT 'materia_prima';

ALTER TABLE PROVEEDORES ADD COLUMN tiempo_entrega_promedio INTEGER NOT NULL
    DEFAULT 0 CHECK (tiempo_entrega_promedio >= 0);

ALTER TABLE PROVEEDORES ADD COLUMN contacto_comercial VARCHAR(100);
ALTER TABLE PROVEEDORES ADD COLUMN contacto_cartera VARCHAR(100);
ALTER TABLE PROVEEDORES ADD COLUMN contacto_logistico VARCHAR(100);

ALTER TABLE PROVEEDORES ADD COLUMN condiciones_pago INTEGER NOT NULL
    DEFAULT 30 CHECK (condiciones_pago >= 0);

ALTER TABLE PROVEEDORES ADD COLUMN calificacion SMALLINT NOT NULL
    DEFAULT 3 CHECK (calificacion BETWEEN 1 AND 5);

ALTER TABLE PROVEEDORES ADD COLUMN ciudad VARCHAR(100);


-- =====================================================================
-- 3. PRODUCTO -> PRODUCTOS (y ajuste a STOCKPRODUCTOS)
-- =====================================================================
ALTER TABLE PRODUCTO RENAME TO PRODUCTOS;

-- eliminación lógica en vez de borrar el registro físico
ALTER TABLE PRODUCTOS ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE;

-- categoría de IVA según la tarifa vigente en Colombia
ALTER TABLE PRODUCTOS ADD COLUMN categoria_iva VARCHAR(20) NOT NULL
    DEFAULT 'general'
    CHECK (categoria_iva IN ('general','diferencial','exento','excluido'));

-- demanda_diaria para poder calcular "días de stock" en la app
-- (el resultado NO se guarda, solo se calcula al consultar)
ALTER TABLE STOCKPRODUCTOS ADD COLUMN demanda_diaria NUMERIC(10,3) NOT NULL
    DEFAULT 0 CHECK (demanda_diaria >= 0);


-- =====================================================================
-- 4. PEDIDO -> FACTURAS
-- =====================================================================
ALTER TABLE PEDIDO RENAME TO FACTURAS;

ALTER TABLE FACTURAS RENAME COLUMN id_pedido TO id_factura;
ALTER TABLE FACTURAS RENAME COLUMN id_usuario TO id_cliente;
ALTER TABLE FACTURAS RENAME COLUMN fecha_pedido TO fecha_expedicion;
ALTER TABLE FACTURAS RENAME COLUMN precio_pedido TO subtotal;

ALTER TABLE FACTURAS ADD COLUMN numero_factura VARCHAR(50) UNIQUE;
ALTER TABLE FACTURAS ADD COLUMN prefijo VARCHAR(10);
ALTER TABLE FACTURAS ADD COLUMN vigencia_resolucion VARCHAR(50);
ALTER TABLE FACTURAS ADD COLUMN hora_generacion TIME;

ALTER TABLE FACTURAS ADD COLUMN valor_iva BIGINT NOT NULL
    DEFAULT 0 CHECK (valor_iva >= 0);

ALTER TABLE FACTURAS ADD COLUMN total_pagar BIGINT NOT NULL
    DEFAULT 0 CHECK (total_pagar >= 0);

ALTER TABLE FACTURAS ADD COLUMN cufe VARCHAR(150);
ALTER TABLE FACTURAS ADD COLUMN codigo_qr TEXT;

-- Nota: PRODUCTOS_ASOCIADOS, HISTORIAL_PEDIDOS, VERIFICAR_PEDIDO,
-- PEDIDO_CONFIRMADO, etc. siguen apuntando a FACTURAS/CLIENTES
-- automáticamente porque Postgres actualiza las FK cuando renombras
-- tablas/columnas. No hay que tocar nada más ahí por ahora.


-- =====================================================================
-- PENDIENTE PARA LA SIGUIENTE RONDA (no lo tocamos todavía):
--  - Crear tabla ORDENES_PEDIDO (compras a proveedores), que hoy
--    no existe en el esquema.
--  - Revisar si PEDIDO_CONFIRMADO / VERIFICAR_PEDIDO siguen teniendo
--    sentido con el nuevo flujo de FACTURAS, o si los simplificamos.
-- =====================================================================
