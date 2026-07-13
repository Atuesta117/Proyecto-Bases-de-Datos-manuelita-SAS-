#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de datos de prueba (seed.sql) para el resto de tablas del esquema,
respetando FKs, CHECKs, UNIQUE y NOT NULL.

Datos YA insertados (no se regeneran):
  - CLIENTES:    CLI-000001 .. CLI-000500   (500)
  - PROVEEDORES: PROV-000001 .. PROV-000200 (200)

Salida: seed.sql  (PostgreSQL)
"""

import random
from datetime import date, timedelta

random.seed(42)  # reproducible

# ------------------------------------------------------------------ #
# Parámetros de volumen ("Grande / realista")
# ------------------------------------------------------------------ #
N_CLIENTES = 500
N_PROVEEDORES = 200
N_SEDES = 10
N_PRODUCTOS = 500
N_ORDENES = 2000
N_PEDIDOS = 2000
N_CAMIONES = 60
N_CONDUCTORES = 80

TODAY = date(2026, 7, 13)


# ------------------------------------------------------------------ #
# Utilidades
# ------------------------------------------------------------------ #
def esc(s):
    """Escapa comillas simples para SQL."""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def num(n):
    if n is None:
        return "NULL"
    return str(n)


def b(v):
    return "TRUE" if v else "FALSE"


def rand_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 0)))


CIUDADES = [
    "Cali",
    "Bogotá",
    "Medellín",
    "Barranquilla",
    "Cartagena",
    "Bucaramanga",
    "Pereira",
    "Manizales",
    "Cúcuta",
    "Ibagué",
]
DEPARTAMENTOS = {
    "Cali": "Valle del Cauca",
    "Bogotá": "Cundinamarca",
    "Medellín": "Antioquia",
    "Barranquilla": "Atlántico",
    "Cartagena": "Bolívar",
    "Bucaramanga": "Santander",
    "Pereira": "Risaralda",
    "Manizales": "Caldas",
    "Cúcuta": "Norte de Santander",
    "Ibagué": "Tolima",
}
BANCOS = [
    "Bancolombia",
    "BBVA",
    "Banco de Bogotá",
    "Davivienda",
    "Banco Popular",
    "Nequi",
]
CATEGORIAS = [
    "Lácteos",
    "Bebidas",
    "Snacks",
    "Aseo",
    "Panadería",
    "Congelados",
    "Enlatados",
    "Granos",
    "Condimentos",
    "Cárnicos",
]
UNIDADES = ["g", "kg", "l", "ml", "galon"]
MARCAS_CAMION = ["Chevrolet", "Hino", "Foton", "JAC", "Kenworth", "Freightliner"]
NOMBRES = [
    "Carlos",
    "Ana",
    "Luis",
    "María",
    "Jorge",
    "Sofía",
    "Andrés",
    "Laura",
    "Diego",
    "Camila",
    "Julián",
    "Valentina",
    "Felipe",
    "Daniela",
]
APELLIDOS = [
    "Gómez",
    "Rodríguez",
    "Martínez",
    "López",
    "García",
    "Pérez",
    "Torres",
    "Ramírez",
    "Vargas",
    "Cruz",
    "Ruiz",
    "Sánchez",
]
TRANSPORTADORAS = ["Servientrega", "Coordinadora", "TCC", "Envía", "Interrapidísimo"]
PAISES = ["Estados Unidos", "México", "Ecuador", "Perú", "España", "Panamá", "Chile"]
DIVISAS = ["USD", "EUR", "MXN", "PEN"]


def cli_id(i):
    return f"CLI-{i:06d}"


def prov_id(i):
    return f"PROV-{i:06d}"


lines = []


def emit(sql):
    lines.append(sql)


def section(title):
    emit(f"\n-- ============================================================")
    emit(f"-- {title}")
    emit(f"-- ============================================================")


emit("-- seed.sql  -- Datos generados automáticamente (PostgreSQL)")
emit("-- Complementa CLIENTES (500) y PROVEEDORES (200) ya insertados.")
emit("BEGIN;")

# ------------------------------------------------------------------ #
# TIPOS_IVA
# ------------------------------------------------------------------ #
section("TIPOS_IVA")
tipos_iva = [
    ("IVA-000001", "Excluido", 0.00),
    ("IVA-000002", "Exento", 0.00),
    ("IVA-000003", "Reducido", 5.00),
    ("IVA-000004", "General", 19.00),
]
for tid, nombre, pct in tipos_iva:
    emit(
        f"INSERT INTO TIPOS_IVA (id_tipo_iva, nombre, porcentaje) VALUES "
        f"({esc(tid)}, {esc(nombre)}, {pct});"
    )
iva_ids = [t[0] for t in tipos_iva]
iva_pct = {t[0]: t[2] for t in tipos_iva}

# ------------------------------------------------------------------ #
# EMPRESA
# ------------------------------------------------------------------ #
section("EMPRESA")
EMPRESA_ID = "EMP-000001"
emit(
    "INSERT INTO EMPRESA (id_empresa, nit, razon_social, nombre_comercial, direccion, "
    "ciudad, telefono, email, representante_legal, tipo_regimen) VALUES ("
    f"{esc(EMPRESA_ID)}, {esc('900123456-7')}, {esc('Distribuidora del Valle S.A.S.')}, "
    f"{esc('DisValle')}, {esc('Cra. 100 # 15-20')}, {esc('Cali')}, {esc('6024851000')}, "
    f"{esc('contacto@disvalle.com.co')}, {esc('Fernando Gómez Ruiz')}, "
    f"{esc('responsable_iva')});"
)

# ------------------------------------------------------------------ #
# SEDES
# ------------------------------------------------------------------ #
section("SEDES")
sede_ids = []
tipos_sede = ["bodega", "planta", "punto_venta", "administrativa"]
for i in range(1, N_SEDES + 1):
    sid = f"SEDE-{i:06d}"
    sede_ids.append(sid)
    ciudad = random.choice(CIUDADES)
    tipo = "administrativa" if i == 1 else random.choice(tipos_sede)
    es_principal = i == 1
    fecha = rand_date(date(2018, 1, 1), date(2024, 12, 31))
    emit(
        "INSERT INTO SEDES (id_sede, id_empresa, nombre_sede, tipo_sede, ciudad, "
        "direccion, telefono, es_principal, fecha_apertura) VALUES ("
        f"{esc(sid)}, {esc(EMPRESA_ID)}, {esc(f'Sede {ciudad} {i}')}, {esc(tipo)}, "
        f"{esc(ciudad)}, {esc(f'Cra. {random.randint(1, 120)} # {random.randint(1, 99)}-{random.randint(1, 99)}')}, "
        f"{esc(f'60{random.randint(2, 8)}{random.randint(1000000, 9999999)}')}, "
        f"{b(es_principal)}, {esc(fecha.isoformat())});"
    )

# ------------------------------------------------------------------ #
# PRODUCTOS
# ------------------------------------------------------------------ #
section("PRODUCTOS")
producto_ids = []
producto_precio = {}
producto_iva = {}  # id_producto -> id_tipo_iva
for i in range(1, N_PRODUCTOS + 1):
    pid = f"PROD-{i:06d}"
    producto_ids.append(pid)
    id_prov = prov_id(random.randint(1, N_PROVEEDORES))
    id_iva = random.choice(iva_ids)
    cat = random.choice(CATEGORIAS)
    precio = random.randint(1000, 500000)
    peso = round(random.uniform(0.05, 25.0), 3)
    unidad = random.choice(UNIDADES)
    activo = random.random() > 0.05
    producto_precio[pid] = precio
    producto_iva[pid] = id_iva
    emit(
        "INSERT INTO PRODUCTOS (id_producto, id_proveedor, id_tipo_iva, nombre, "
        "descripcion, precio, categoria, peso, unidad_medida, activo) VALUES ("
        f"{esc(pid)}, {esc(id_prov)}, {esc(id_iva)}, {esc(f'{cat} {i}')}, "
        f"{esc(f'Producto {cat.lower()} referencia {i}')}, {precio}, {esc(cat)}, "
        f"{peso}, {esc(unidad)}, {b(activo)});"
    )

# ------------------------------------------------------------------ #
# STOCKPRODUCTOS (1 por producto)
# ------------------------------------------------------------------ #
section("STOCKPRODUCTOS")
for i, pid in enumerate(producto_ids, start=1):
    disponible = random.randint(0, 5000)
    reservada = random.randint(0, disponible) if disponible > 0 else 0
    minimo = random.randint(10, 500)
    demanda = round(random.uniform(0, 200), 3)
    emit(
        "INSERT INTO STOCKPRODUCTOS (id_stock, id_producto, cantidad_disponible, "
        "cantidad_reservada, stock_minimo, demanda_diaria) VALUES ("
        f"{esc(f'STK-{i:06d}')}, {esc(pid)}, {disponible}, {reservada}, {minimo}, {demanda});"
    )

# ------------------------------------------------------------------ #
# ORDENES_PEDIDO_PROVEEDOR + DETALLE
# ------------------------------------------------------------------ #
section("ORDENES_PEDIDO_PROVEEDOR")
estados_orden = ["pendiente", "en_transito", "recibido", "cancelado"]
detalle_orden_recibidos = []  # (id_detalle_orden, id_producto, id_proveedor, id_sede)
det_orden_counter = 0
for i in range(1, N_ORDENES + 1):
    oid = f"OPP-{i:06d}"
    id_sede = random.choice(sede_ids)
    id_prov = prov_id(random.randint(1, N_PROVEEDORES))
    estado = random.choices(estados_orden, weights=[15, 20, 55, 10])[0]
    fecha = rand_date(date(2024, 1, 1), TODAY)
    ciudad = random.choice(CIUDADES)
    emit(
        "INSERT INTO ORDENES_PEDIDO_PROVEEDOR (id_orden, id_sede, id_proveedor, "
        "fecha_pedido, lugar_entrega, estado) VALUES ("
        f"{esc(oid)}, {esc(id_sede)}, {esc(id_prov)}, {esc(fecha.isoformat())}, "
        f"{esc(f'Bodega {ciudad}')}, {esc(estado)});"
    )
    # detalle: 1-4 productos distintos por orden
    prods = random.sample(producto_ids, random.randint(1, 4))
    for pid in prods:
        det_orden_counter += 1
        did = f"DOPP-{det_orden_counter:07d}"
        cantidad = random.randint(10, 1000)
        costo = random.randint(500, 400000)
        emit(
            "INSERT INTO DETALLE_ORDEN_PEDIDO_PROVEEDOR (id_detalle_orden, id_orden, "
            "id_producto, cantidad, costo_unitario) VALUES ("
            f"{esc(did)}, {esc(oid)}, {esc(pid)}, {cantidad}, {costo});"
        )
        if estado == "recibido":
            detalle_orden_recibidos.append((did, pid, id_prov, id_sede))

# ------------------------------------------------------------------ #
# LOTES
# ------------------------------------------------------------------ #
section("LOTES")
lotes_por_producto = {}  # id_producto -> [id_lote,...]
lote_counter = 0


def add_lote(pid, id_prov, id_sede, id_detalle_orden):
    global lote_counter
    lote_counter += 1
    lid = f"LOTE-{lote_counter:07d}"
    fecha_ing = rand_date(date(2024, 1, 1), TODAY)
    fecha_ven = fecha_ing + timedelta(days=random.randint(30, 720))
    cant_ini = random.randint(50, 2000)
    cant_act = random.randint(0, cant_ini)
    emit(
        "INSERT INTO LOTES (id_lote, id_producto, id_proveedor, id_sede, "
        "id_detalle_orden, fecha_ingreso, fecha_vencimiento, cantidad_inicial, "
        "cantidad_actual) VALUES ("
        f"{esc(lid)}, {esc(pid)}, {esc(id_prov)}, {esc(id_sede)}, "
        f"{esc(id_detalle_orden)}, {esc(fecha_ing.isoformat())}, "
        f"{esc(fecha_ven.isoformat())}, {cant_ini}, {cant_act});"
    )
    lotes_por_producto.setdefault(pid, []).append(lid)


# Un lote por cada detalle de orden recibida (vinculado a la orden)
for did, pid, id_prov, id_sede in detalle_orden_recibidos:
    add_lote(pid, id_prov, id_sede, did)

# Garantizar que TODO producto tenga al menos un lote (sin detalle_orden -> NULL)
for pid in producto_ids:
    if pid not in lotes_por_producto:
        id_prov = prov_id(random.randint(1, N_PROVEEDORES))
        id_sede = random.choice(sede_ids)
        add_lote(pid, id_prov, id_sede, None)

# ------------------------------------------------------------------ #
# PEDIDO + DETALLE_PEDIDO
# ------------------------------------------------------------------ #
section("PEDIDO")
estados_pedido = ["pendiente", "verificado", "confirmado", "rechazado", "anulado"]
detalle_pedido_por_pedido = {}  # id_pedido -> [(id_detalle_pedido, id_producto, cantidad)]
pedido_estado = {}
det_pedido_counter = 0
for i in range(1, N_PEDIDOS + 1):
    pid_ped = f"PED-{i:06d}"
    id_cli = cli_id(random.randint(1, N_CLIENTES))
    estado = random.choices(estados_pedido, weights=[15, 15, 45, 15, 10])[0]
    pedido_estado[pid_ped] = estado
    fecha = rand_date(date(2024, 6, 1), TODAY)
    emit(
        "INSERT INTO PEDIDO (id_pedido, id_cliente, fecha_pedido, estado, observaciones) "
        f"VALUES ({esc(pid_ped)}, {esc(id_cli)}, {esc(fecha.isoformat() + ' 10:00:00')}, "
        f"{esc(estado)}, {esc('Pedido generado automáticamente') if random.random() > 0.5 else 'NULL'});"
    )
    prods = random.sample(producto_ids, random.randint(1, 5))
    dets = []
    for pid in prods:
        det_pedido_counter += 1
        did = f"DPED-{det_pedido_counter:07d}"
        cantidad = random.randint(1, 50)
        dets.append((did, pid, cantidad))
        emit(
            "INSERT INTO DETALLE_PEDIDO (id_detalle_pedido, id_pedido, id_producto, "
            "cantidad_solicitada) VALUES ("
            f"{esc(did)}, {esc(pid_ped)}, {esc(pid)}, {cantidad});"
        )
    detalle_pedido_por_pedido[pid_ped] = dets

# ------------------------------------------------------------------ #
# DETALLE_PEDIDO_LOTE (asignar un lote del mismo producto)
# ------------------------------------------------------------------ #
section("DETALLE_PEDIDO_LOTE")
asig_counter = 0
for pid_ped, dets in detalle_pedido_por_pedido.items():
    for did, pid, cantidad in dets:
        lotes = lotes_por_producto.get(pid)
        if not lotes:
            continue
        lid = random.choice(lotes)
        asig_counter += 1
        emit(
            "INSERT INTO DETALLE_PEDIDO_LOTE (id_asignacion, id_detalle_pedido, id_lote, "
            "cantidad_asignada) VALUES ("
            f"{esc(f'DPL-{asig_counter:07d}')}, {esc(did)}, {esc(lid)}, {cantidad});"
        )

# ------------------------------------------------------------------ #
# VERIFICAR_PEDIDO (1 por pedido verificado/confirmado/rechazado)
# ------------------------------------------------------------------ #
section("VERIFICAR_PEDIDO")
verificacion_de_pedido = {}  # id_pedido -> (id_verificacion, esValido)
ver_counter = 0
for pid_ped, estado in pedido_estado.items():
    if estado in ("verificado", "confirmado", "rechazado"):
        ver_counter += 1
        vid = f"VER-{ver_counter:06d}"
        es_valido = estado != "rechazado"
        verificacion_de_pedido[pid_ped] = (vid, es_valido)
        fecha = rand_date(date(2024, 6, 1), TODAY)
        obs = "Verificación OK" if es_valido else "Pedido rechazado por inconsistencias"
        emit(
            "INSERT INTO VERIFICAR_PEDIDO (id_verificacion, id_pedido, fecha_verificacion, "
            "esValido, observaciones) VALUES ("
            f"{esc(vid)}, {esc(pid_ped)}, {esc(fecha.isoformat())}, {b(es_valido)}, {esc(obs)});"
        )

# ------------------------------------------------------------------ #
# FACTURAS + DETALLE_FACTURA + PEDIDO_CONFIRMADO
#   Solo para pedidos 'confirmado' con verificación válida.
# ------------------------------------------------------------------ #
section("FACTURAS / DETALLE_FACTURA / PEDIDO_CONFIRMADO")
metodos_pago = ["efectivo", "tarjeta", "transferencia", "contraentrega"]
fact_counter = 0
det_fact_counter = 0
conf_counter = 0
confirmaciones = []  # (id_confirmacion, id_factura, id_cliente, fecha)
for pid_ped, estado in pedido_estado.items():
    if estado != "confirmado":
        continue
    ver = verificacion_de_pedido.get(pid_ped)
    if not ver or not ver[1]:
        continue
    vid, _ = ver
    dets = detalle_pedido_por_pedido[pid_ped]
    # Factura
    fact_counter += 1
    fid = f"FAC-{fact_counter:06d}"
    id_cli = cli_id(random.randint(1, N_CLIENTES))
    fecha = rand_date(date(2024, 6, 1), TODAY)
    subtotal = 0
    total_iva = 0
    item_rows = []
    for did, pid, cantidad in dets:
        precio = producto_precio[pid]
        pct = iva_pct[producto_iva[pid]]
        sub_item = precio * cantidad
        v_iva = int(round(sub_item * pct / 100))
        tot_item = sub_item + v_iva
        subtotal += sub_item
        total_iva += v_iva
        det_fact_counter += 1
        item_rows.append(
            "INSERT INTO DETALLE_FACTURA (id_detalle, id_factura, id_producto, cantidad, "
            "precio_unitario, porcentaje_iva, valor_iva, subtotal_item, total_item) VALUES ("
            f"{esc(f'DFAC-{det_fact_counter:07d}')}, {esc(fid)}, {esc(pid)}, {cantidad}, "
            f"{precio}, {pct}, {v_iva}, {sub_item}, {tot_item});"
        )
    total_pagar = subtotal + total_iva
    metodo = random.choice(metodos_pago)
    prefijo = "FE"
    num_fact = f"{prefijo}-{fact_counter:07d}"
    emit(
        "INSERT INTO FACTURAS (id_factura, id_empresa, id_cliente, numero_factura, prefijo, "
        "vigencia_resolucion, fecha_generacion, fecha_expedicion, metodo_pago, estado, "
        "subtotal, valor_iva, total_pagar, cufe, codigo_qr) VALUES ("
        f"{esc(fid)}, {esc(EMPRESA_ID)}, {esc(id_cli)}, {esc(num_fact)}, {esc(prefijo)}, "
        f"{esc('Res. DIAN 18760000001 vigente 2024-2026')}, "
        f"{esc(fecha.isoformat() + ' 09:00:00')}, {esc(fecha.isoformat() + ' 09:05:00')}, "
        f"{esc(metodo)}, {esc('confirmado')}, {subtotal}, {total_iva}, {total_pagar}, "
        f"{esc('CUFE' + str(random.randint(10**14, 10**15)))}, {esc('QR-' + fid)});"
    )
    for r in item_rows:
        emit(r)
    # PEDIDO_CONFIRMADO
    conf_counter += 1
    cfid = f"CONF-{conf_counter:06d}"
    fecha_conf = fecha + timedelta(days=random.randint(0, 3))
    if fecha_conf > TODAY:
        fecha_conf = TODAY
    emit(
        "INSERT INTO PEDIDO_CONFIRMADO (id_confirmacion, id_verificacion, id_factura, "
        "fecha_confirmacion, esValido) VALUES ("
        f"{esc(cfid)}, {esc(vid)}, {esc(fid)}, {esc(fecha_conf.isoformat())}, TRUE);"
    )
    confirmaciones.append((cfid, fid, id_cli, fecha_conf))

# ------------------------------------------------------------------ #
# CAMION
# ------------------------------------------------------------------ #
section("CAMION")
camiones_por_sede = {}  # id_sede -> [id_camion]
camion_ids = []
estados_camion = ["disponible", "en_ruta", "mantenimiento", "fuera_de_servicio"]
placas_seen = set()


def gen_placa():
    L = "ABCDEFGHJKLMNP"
    while True:
        p = f"{random.choice(L)}{random.choice(L)}{random.choice(L)}{random.randint(100, 999)}"
        if p not in placas_seen:
            placas_seen.add(p)
            return p


for i in range(1, N_CAMIONES + 1):
    cid = f"CAM-{i:06d}"
    camion_ids.append(cid)
    id_sede = random.choice(sede_ids)
    camiones_por_sede.setdefault(id_sede, []).append(cid)
    placa = gen_placa()
    emit(
        "INSERT INTO CAMION (id_camion, id_sede, placa, marca, modelo, capacidad_kg, "
        "estado, kilometraje) VALUES ("
        f"{esc(cid)}, {esc(id_sede)}, {esc(placa)}, {esc(random.choice(MARCAS_CAMION))}, "
        f"{esc(str(random.randint(2015, 2025)))}, {round(random.uniform(1000, 20000), 3)}, "
        f"{esc(random.choice(estados_camion))}, {random.randint(0, 400000)});"
    )

# ------------------------------------------------------------------ #
# CONDUCTOR
# ------------------------------------------------------------------ #
section("CONDUCTOR")
conductor_ids = []
ced_seen = set()
lic_seen = set()


def gen_unique(seen, fn):
    while True:
        v = fn()
        if v not in seen:
            seen.add(v)
            return v


for i in range(1, N_CONDUCTORES + 1):
    cid = f"COND-{i:06d}"
    conductor_ids.append(cid)
    id_sede = random.choice(sede_ids)
    ced = gen_unique(ced_seen, lambda: str(random.randint(10000000, 1999999999)))
    lic = gen_unique(lic_seen, lambda: f"LIC{random.randint(100000, 999999)}")
    venc = rand_date(TODAY, date(2030, 12, 31))
    emit(
        "INSERT INTO CONDUCTOR (id_conductor, id_sede, nombre, apellido, cedula, telefono, "
        "licencia, fecha_vencimiento_licencia, disponible) VALUES ("
        f"{esc(cid)}, {esc(id_sede)}, {esc(random.choice(NOMBRES))}, "
        f"{esc(random.choice(APELLIDOS))}, {esc(ced)}, {esc('3' + str(random.randint(100000000, 199999999)))}, "
        f"{esc(lic)}, {esc(venc.isoformat())}, {b(random.random() > 0.3)});"
    )

# ------------------------------------------------------------------ #
# CAMION_CONDUCTOR
# ------------------------------------------------------------------ #
section("CAMION_CONDUCTOR")
cc_counter = 0
for cid in camion_ids:
    # 1-2 conductores por camión, fechas distintas
    n = random.randint(1, 2)
    conds = random.sample(conductor_ids, n)
    fecha_ini = rand_date(date(2023, 1, 1), date(2025, 6, 1))
    for k, cond in enumerate(conds):
        cc_counter += 1
        fi = fecha_ini + timedelta(days=k * 200)
        cerrar = random.random() > 0.5
        ff = (fi + timedelta(days=random.randint(30, 180))) if cerrar else None
        emit(
            "INSERT INTO CAMION_CONDUCTOR (id_camion_conductor, id_camion, id_conductor, "
            "fecha_inicio, fecha_fin) VALUES ("
            f"{esc(f'CC-{cc_counter:07d}')}, {esc(cid)}, {esc(cond)}, "
            f"{esc(fi.isoformat())}, {esc(ff.isoformat()) if ff else 'NULL'});"
        )

# ------------------------------------------------------------------ #
# ENVIOS + subtipos + ASIGNACION_CAMIONES
#   Un envío por cada pedido confirmado (id_pedido_confirmado UNIQUE).
# ------------------------------------------------------------------ #
section("ENVIOS / ENVIO_NACIONAL / ENVIO_INTERNACIONAL / ASIGNACION_CAMIONES")
estados_envio = ["preparando", "en_camino", "entregado", "devuelto"]
env_counter = 0
asigc_counter = 0
tracking_seen = set()
for cfid, fid, id_cli, fecha_conf in confirmaciones:
    env_counter += 1
    eid = f"ENV-{env_counter:06d}"
    id_sede_origen = random.choice(sede_ids)
    fecha_envio = fecha_conf
    fecha_est = fecha_envio + timedelta(days=random.randint(1, 15))
    tipo = random.choices(["nacional", "internacional"], weights=[85, 15])[0]
    ciudad_dest = random.choice(CIUDADES)
    emit(
        "INSERT INTO ENVIOS (id_envio, id_pedido_confirmado, id_sede_origen, direccion_origen, "
        "direccion_destino, fecha_envio, fecha_entrega_estimada, estado_envio, tipo_envio) VALUES ("
        f"{esc(eid)}, {esc(cfid)}, {esc(id_sede_origen)}, {esc('Bodega central Cali')}, "
        f"{esc(f'Cra. {random.randint(1, 120)} # {random.randint(1, 99)}-{random.randint(1, 99)}, {ciudad_dest}')}, "
        f"{esc(fecha_envio.isoformat())}, {esc(fecha_est.isoformat())}, "
        f"{esc(random.choice(estados_envio))}, {esc(tipo)});"
    )
    if tipo == "nacional":
        emit(
            "INSERT INTO ENVIO_NACIONAL (id_envio, departamento, ciudad, codigo_postal, "
            "transportadora_local) VALUES ("
            f"{esc(eid)}, {esc(DEPARTAMENTOS[ciudad_dest])}, {esc(ciudad_dest)}, "
            f"{esc(str(random.randint(50000, 999999)).zfill(6))}, {esc(random.choice(TRANSPORTADORAS))});"
        )
    else:
        # tracking único
        tk = f"INTL{random.randint(10**9, 10**10)}"
        while tk in tracking_seen:
            tk = f"INTL{random.randint(10**9, 10**10)}"
        tracking_seen.add(tk)
        emit(
            "INSERT INTO ENVIO_INTERNACIONAL (id_envio, pais_destino, aduana, "
            "numero_tracking_internacional, costo_aduana, divisa) VALUES ("
            f"{esc(eid)}, {esc(random.choice(PAISES))}, {esc('Aduana ' + random.choice(CIUDADES))}, "
            f"{esc(tk)}, {round(random.uniform(50, 5000), 2)}, {esc(random.choice(DIVISAS))});"
        )
    # Asignar 1 camión (preferiblemente de la sede de origen)
    posibles = camiones_por_sede.get(id_sede_origen) or camion_ids
    cam = random.choice(posibles)
    asigc_counter += 1
    emit(
        "INSERT INTO ASIGNACION_CAMIONES (id_envio_camion_nor, id_envio, id_camion, fecha_carga) "
        f"VALUES ({esc(f'AC-{asigc_counter:07d}')}, {esc(eid)}, {esc(cam)}, "
        f"{esc(fecha_envio.isoformat())});"
    )

emit("\nCOMMIT;")

# ------------------------------------------------------------------ #
with open("seed.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"seed.sql generado: {len(lines)} lineas")
print(f"  TIPOS_IVA={len(tipos_iva)} EMPRESA=1 SEDES={N_SEDES} PRODUCTOS={N_PRODUCTOS}")
print(f"  STOCK={N_PRODUCTOS} ORDENES={N_ORDENES} DETALLE_ORDEN={det_orden_counter}")
print(f"  LOTES={lote_counter} PEDIDOS={N_PEDIDOS} DETALLE_PEDIDO={det_pedido_counter}")
print(
    f"  VERIFICACIONES={ver_counter} FACTURAS={fact_counter} DETALLE_FACTURA={det_fact_counter}"
)
print(
    f"  CONFIRMACIONES={conf_counter} ENVIOS={env_counter} ASIGNACIONES={asigc_counter}"
)
print(
    f"  CAMIONES={N_CAMIONES} CONDUCTORES={N_CONDUCTORES} CAMION_CONDUCTOR={cc_counter}"
)
