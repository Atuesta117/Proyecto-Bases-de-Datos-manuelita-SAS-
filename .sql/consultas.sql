-- 1. Listado de productos activos de la compañía con su precio y categoría
-- Filtro añadido al SELECT: activo
SELECT 
    nombre, 
    categoria, 
    precio, 
    unidad_medida,
    activo
FROM PRODUCTOS
WHERE activo = TRUE;

-- 2. Distribución geográfica de clientes que han aceptado políticas de datos
-- Filtro añadido a la consulta y al SELECT: habeas_data
SELECT 
    ciudad, 
    habeas_data,
    COUNT(id_cliente) AS total_clientes
FROM CLIENTES
WHERE habeas_data = TRUE
GROUP BY ciudad, habeas_data
ORDER BY total_clientes DESC;

-- 3. Productos con alerta de stock crítico
-- Filtros en el SELECT: cantidad_disponible y stock_minimo (ya estaban, pero son los que operan el filtro)
SELECT 
    id_producto, 
    cantidad_disponible, 
    stock_minimo
FROM STOCKPRODUCTOS
WHERE cantidad_disponible < stock_minimo;

-- 4. Estado actual de la flota logística que pertenece a una sede específica
-- Filtro añadido a la consulta y al SELECT: id_sede (para omitir camiones sin sede asignada) y estado
SELECT 
    id_sede,
    estado, 
    COUNT(id_camion) AS cantidad_camiones
FROM CAMION
WHERE id_sede IS NOT NULL
GROUP BY id_sede, estado;

-- 5. Seguimiento a órdenes de pedido a proveedores que siguen "pendientes"
-- Filtro añadido al SELECT: estado
SELECT 
    id_orden, 
    id_proveedor, 
    fecha_pedido, 
    lugar_entrega,
    estado
FROM ORDENES_PEDIDO_PROVEEDOR
WHERE estado = 'pendiente'
ORDER BY fecha_pedido ASC;

-- 6. Total facturado por cada cliente (Top clientes según sus facturas confirmadas)
-- Filtro añadido al SELECT: f.estado
SELECT 
    c.nombre_razon_social, 
    c.numero_identificacion, 
    f.estado,
    SUM(f.total_pagar) AS total_comprado
FROM CLIENTES c
JOIN FACTURAS f ON c.id_cliente = f.id_cliente
WHERE f.estado = 'confirmado'
GROUP BY c.id_cliente, c.nombre_razon_social, c.numero_identificacion, f.estado
ORDER BY total_comprado DESC;

-- 7. Lotes de inventario próximos a vencer en los siguientes 30 días
-- Filtros en el SELECT: l.fecha_vencimiento y l.cantidad_actual (visibles para validar la lógica del WHERE)
SELECT 
    l.id_lote, 
    p.nombre AS producto, 
    prov.nombre_razon_social AS proveedor, 
    l.fecha_vencimiento, 
    l.cantidad_actual
FROM LOTES l
JOIN PRODUCTOS p ON l.id_producto = p.id_producto
JOIN PROVEEDORES prov ON l.id_proveedor = prov.id_proveedor
WHERE l.cantidad_actual > 0 
  AND l.fecha_vencimiento <= CURRENT_DATE + INTERVAL '30 days'
ORDER BY l.fecha_vencimiento ASC;

-- 8. Rastreo logístico: Detalle completo de los envíos en tránsito
-- Filtro añadido al SELECT: e.estado_envio
SELECT 
    e.id_envio, 
    c.nombre_razon_social AS cliente, 
    e.direccion_destino, 
    p.nombre AS producto, 
    dp.cantidad_solicitada,
    e.estado_envio
FROM ENVIOS e
JOIN PEDIDO_CONFIRMADO pc ON e.id_pedido_confirmado = pc.id_confirmacion
JOIN VERIFICAR_PEDIDO vp ON pc.id_verificacion = vp.id_verificacion
JOIN PEDIDO ped ON vp.id_pedido = ped.id_pedido
JOIN CLIENTES c ON ped.id_cliente = c.id_cliente
JOIN DETALLE_PEDIDO dp ON ped.id_pedido = dp.id_pedido
JOIN PRODUCTOS p ON dp.id_producto = p.id_producto
WHERE e.estado_envio = 'en_camino';

-- 9. Asignación actual de flota (relaciones activas sin fecha de fin)
-- Filtro añadido al SELECT: cc.fecha_fin
SELECT 
    cond.nombre, 
    cond.apellido, 
    cond.licencia, 
    cam.placa, 
    cam.marca, 
    s.nombre_sede AS sede_origen,
    cc.fecha_inicio,
    cc.fecha_fin
FROM CONDUCTOR cond
JOIN CAMION_CONDUCTOR cc ON cond.id_conductor = cc.id_conductor
JOIN CAMION cam ON cc.id_camion = cam.id_camion
JOIN SEDES s ON cond.id_sede = s.id_sede
WHERE cc.fecha_fin IS NULL; 

-- 10. Análisis de desabastecimiento vs pedidos pendientes
-- Filtro en el SELECT: sp.cantidad_disponible (y muestro la demanda calculada contra la que se compara)
SELECT 
    p.nombre, 
    p.categoria, 
    sp.cantidad_disponible,
    (SELECT COALESCE(SUM(dp.cantidad_solicitada), 0)
     FROM DETALLE_PEDIDO dp
     JOIN PEDIDO ped ON dp.id_pedido = ped.id_pedido
     WHERE dp.id_producto = p.id_producto AND ped.estado = 'pendiente') AS demanda_pendiente_total
FROM PRODUCTOS p
JOIN STOCKPRODUCTOS sp ON p.id_producto = sp.id_producto
WHERE sp.cantidad_disponible < (
    SELECT COALESCE(SUM(dp.cantidad_solicitada), 0)
    FROM DETALLE_PEDIDO dp
    JOIN PEDIDO ped ON dp.id_pedido = ped.id_pedido
    WHERE dp.id_producto = p.id_producto AND ped.estado = 'pendiente'
);
-- 11. Listar todos los proveedores de tipo "materia_prima"
SELECT nombre_razon_social, ciudad, tiempo_entrega_promedio, tipo_proveedor
FROM proveedores
WHERE tipo_proveedor = 'materia_prima';

-- 12. Productos activos ordenados por precio descendente
SELECT nombre, precio, categoria, activo
FROM productos
WHERE activo = true
ORDER BY precio DESC;

-- 13. Clientes que aceptaron habeas data
SELECT nombre_razon_social, email, ciudad, habeas_data
FROM clientes
WHERE habeas_data = true;

-- 14. Camiones disponibles
SELECT placa, marca, modelo, capacidad_kg, estado
FROM camion
WHERE estado = 'disponible';

-- 15. Facturas anuladas
SELECT numero_factura, fecha_expedicion, total_pagar, estado
FROM facturas
WHERE estado = 'anulada';
-- 16. Ranking de clientes por total facturado, con su posición (window function)
SELECT
    c.nombre_razon_social,
    SUM(f.total_pagar) AS total_facturado,
    RANK() OVER (ORDER BY SUM(f.total_pagar) DESC) AS posicion
FROM facturas f
JOIN clientes c ON f.id_cliente = c.id_cliente
GROUP BY c.nombre_razon_social;
-- (ya trae total_facturado y posicion visibles, no requiere ajuste)

-- 17. Productos cuyo stock actual está por debajo del punto de reorden
SELECT
    p.nombre,
    s.cantidad_disponible,
    s.demanda_diaria,
    pr.tiempo_entrega_promedio,
    ROUND(s.demanda_diaria * pr.tiempo_entrega_promedio, 1) AS punto_reorden
FROM productos p
JOIN stockproductos s ON p.id_producto = s.id_producto
JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
WHERE s.cantidad_disponible < (s.demanda_diaria * pr.tiempo_entrega_promedio);
-- (se agregan demanda_diaria y tiempo_entrega_promedio, que son los factores del WHERE)

-- 18. Clientes que NUNCA han hecho un pedido (subconsulta con NOT EXISTS)
SELECT c.id_cliente, c.nombre_razon_social
FROM clientes c
WHERE NOT EXISTS (
    SELECT 1 FROM pedido pe WHERE pe.id_cliente = c.id_cliente
);
-- (aquí no aplica agregar columna: el filtro es "no existe fila relacionada",
--  no un valor de una columna propia de clientes)

-- 19. Top 3 productos más vendidos por cantidad total, con su facturación total
SELECT
    pr.nombre,
    SUM(df.cantidad) AS unidades_vendidas,
    SUM(df.total_item) AS ingresos_totales
FROM detalle_factura df
JOIN productos pr ON df.id_producto = pr.id_producto
GROUP BY pr.nombre
ORDER BY unidades_vendidas DESC
LIMIT 3;
-- (ya trae unidades_vendidas visible, que es el criterio de orden, no requiere ajuste)

-- 20. Envíos retrasados: fecha estimada ya pasó y no están "entregado"
SELECT
    e.id_envio,
    c.nombre_razon_social,
    e.fecha_entrega_estimada,
    e.estado_envio,
    CURRENT_DATE - e.fecha_entrega_estimada AS dias_de_retraso
FROM envios e
JOIN pedido_confirmado pc ON e.id_pedido_confirmado = pc.id_confirmacion
JOIN verificar_pedido vp ON pc.id_verificacion = vp.id_verificacion
JOIN pedido pe ON vp.id_pedido = pe.id_pedido
JOIN clientes c ON pe.id_cliente = c.id_cliente
WHERE e.estado_envio != 'entregado'
  AND e.fecha_entrega_estimada < CURRENT_DATE;
-- (ya trae estado_envio y fecha_entrega_estimada visibles, que son los dos factores del WHERE)
