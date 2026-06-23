-- CONSULTA 1: Ventas Totales e Impacto en Transporte por Categoría de Producto
-- Objetivo: Mostrar qué categorías generan más volumen de pedidos y demandan mayor peso de carga.
SELECT 
    p.categoria,
    COUNT(pa.id_productos_asociados) AS total_lineas_vendidas,
    SUM(pa.cantidad) AS total_unidades_vendidas,
    SUM(pa.cantidad * p.peso) AS peso_total_despachado_kg
FROM PRODUCTOS_ASOCIADOS pa
JOIN PRODUCTO p ON pa.id_producto = p.id_producto
GROUP BY p.categoria
ORDER BY total_unidades_vendidas DESC;


-- CONSULTA 2: Detección de los Productos Más Populares
-- Objetivo: Identificar el TOP 10 de productos con mayor rotación y volumen de salida.
SELECT 
    p.id_producto,
    p.nombre,
    p.precio,
    SUM(pa.cantidad) AS unidades_vendidas_totales,
    COUNT(DISTINCT pa.id_pedido) AS numero_de_pedidos_donde_aparece
FROM PRODUCTOS_ASOCIADOS pa
JOIN PRODUCTO p ON pa.id_producto = p.id_producto
GROUP BY p.id_producto, p.nombre, p.precio
ORDER BY unidades_vendidas_totales DESC
LIMIT 10;


-- CONSULTA 3: Estacionalidad y Análisis Temporal de Pedidos
-- Objetivo: Agrupar pedidos por mes/año para demostrar los picos de ventas de la simulación.
SELECT 
    EXTRACT(YEAR FROM pe.fecha_pedido) AS anio,
    EXTRACT(MONTH FROM pe.fecha_pedido) AS mes,
    COUNT(pe.id_pedido) AS cantidad_pedidos,
    SUM(pe.precio_pedido) AS monto_total_pedidos,
    SUM(pe.precio_envio) AS recaudacion_envios
FROM PEDIDO pe
GROUP BY EXTRACT(YEAR FROM pe.fecha_pedido), EXTRACT(MONTH FROM pe.fecha_pedido)
ORDER BY anio DESC, mes ASC;


-- CONSULTA 4: Resumen de Desempeño Operativo y Costos: Internacional vs Nacional
-- Objetivo: Comparar tiempos estimados de entrega y costos aduaneros adicionales por tipo de envío.
SELECT 
    e.tipo_envio,
    COUNT(e.id_envio) AS total_envios,
    AVG(e.fecha_entrega_estimada - e.fecha_envio) AS dias_promedio_estimados_entrega,
    SUM(COALESCE(ei.costo_aduana, 0)) AS costos_totales_aduana
FROM ENVIOS e
LEFT JOIN ENVIO_INTERNACIONAL ei ON e.id_envio = ei.id_envio
GROUP BY e.tipo_envio;


-- CONSULTA 5: Alerta de Caducidad de Lotes en Inventario Activo
-- Objetivo: Mostrar los productos con existencias disponibles que vencerán pronto (menos de 30 días).
SELECT 
    p.id_producto,
    p.nombre AS producto,
    l.id_lote,
    l.fecha_vencimiento,
    sp.cantidad_disponible,
    (l.fecha_vencimiento - CURRENT_DATE) AS dias_para_vencer
FROM PRODUCTO p
JOIN LOTES l ON p.id_lote = l.id_lote
JOIN STOCKPRODUCTOS sp ON p.id_producto = sp.id_producto
WHERE (l.fecha_vencimiento - CURRENT_DATE) <= 30 AND sp.cantidad_disponible > 0
ORDER BY l.fecha_vencimiento ASC;


-- CONSULTA 6: Ranking de Clientes VIP y Métodos de Pago Preferidos
-- Objetivo: Listar los 5 clientes que más han gastado en pedidos y su modalidad de pago principal.
SELECT 
    u.id_usuario,
    u.nombre,
    u.apellido,
    COUNT(pe.id_pedido) AS total_pedidos_realizados,
    SUM(pe.precio_pedido) AS total_dinero_gastado,
    MODE() WITHIN GROUP (ORDER BY pe.metodo_pago) AS metodo_pago_mas_usado
FROM USUARIOS u
JOIN PEDIDO pe ON u.id_usuario = pe.id_usuario
WHERE pe.estado = 'entregado'
GROUP BY u.id_usuario, u.nombre, u.apellido
ORDER BY total_dinero_gastado DESC
LIMIT 5;


-- CONSULTA 7: Uso Operativo y Capacidad de la Flota de Camiones
-- Objetivo: Rastrear cuántos envíos han sido asignados a cada vehículo y su kilometraje actual.
SELECT 
    c.id_camion,
    c.placa,
    c.marca,
    c.capacidad_kg,
    COUNT(ac.id_envio_camion_nor) AS envios_asignados,
    c.estado AS estado_actual_camion
FROM CAMION c
LEFT JOIN ASIGNACION_CAMIONES ac ON c.id_camion = ac.id_camion
GROUP BY c.id_camion, c.placa, c.marca, c.capacidad_kg, c.estado
ORDER BY envios_asignados DESC;


-- CONSULTA 8: Nivel de Abastecimiento Crítico por Proveedor
-- Objetivo: Cuantificar qué volumen de stock actual en bodega proviene de cada empresa proveedora.
SELECT 
    pr.id_proveedor,
    pr.nombre_empresa,
    COUNT(DISTINCT p.id_producto) AS variedad_productos,
    SUM(sp.cantidad_disponible) AS stock_total_en_bodega
FROM PROVEEDOR pr
JOIN LOTES l ON pr.id_proveedor = l.id_proveedor
JOIN PRODUCTO p ON l.id_lote = p.id_lote
JOIN STOCKPRODUCTOS sp ON p.id_producto = sp.id_producto
GROUP BY pr.id_proveedor, pr.nombre_empresa
ORDER BY stock_total_en_bodega DESC;


-- CONSULTA 9: Análisis de Diversificación y Recurrencia de Clientes
-- Objetivo: Identificar los clientes corporativos que compran múltiples categorías 
-- de productos (ej. Azúcar y Biocombustibles), evaluando su ticket promedio de compra.
SELECT 
    u.id_usuario,
    u.nombre AS empresa_cliente,
    u.apellido AS marca_grupo,
    COUNT(DISTINCT p.categoria) AS categorias_distintas_compradas,
    COUNT(DISTINCT pe.id_pedido) AS total_pedidos_realizados,
    ROUND(AVG(pe.precio_pedido), 2) AS ticket_promedio_precio_pedido
FROM USUARIOS u
JOIN PEDIDO pe ON u.id_usuario = pe.id_usuario
JOIN PRODUCTOS_ASOCIADOS pa ON pe.id_pedido = pa.id_pedido
JOIN PRODUCTO p ON pa.id_producto = p.id_producto
GROUP BY u.id_usuario, u.nombre, u.apellido
HAVING COUNT(DISTINCT p.categoria) >= 2
ORDER BY total_pedidos_realizados DESC;


-- CONSULTA 10: Auditoría y Trazabilidad de Historial de Estados de Pedidos
-- Objetivo: Cruzar los pedidos con su historial normalizado para ver cuántas veces han cambiado de estado.
SELECT 
    pe.id_pedido,
    pe.fecha_pedido AS fecha_origen,
    pe.estado AS estado_actual,
    COUNT(hpn.id_historial_nor) AS total_cambios_de_estado
FROM PEDIDO pe
LEFT JOIN HISTORIAL_PEDIDOS_NOR hpn ON pe.id_pedido = hpn.id_pedido
GROUP BY pe.id_pedido, pe.fecha_pedido, pe.estado
ORDER BY total_cambios_de_estado DESC;
