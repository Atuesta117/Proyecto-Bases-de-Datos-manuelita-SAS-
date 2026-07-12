# Guía de instalación y ejecución del proyecto

Esta guía asume que ya clonaste el repositorio y estás parado en la carpeta raíz del proyecto (donde está el `.gitignore`, `requirements.txt`, etc.).

Requisitos previos: tener instalado **Python 3.10+**, **PostgreSQL** y **git**.

---

## 1. Crear el entorno virtual

El entorno virtual (`venv`) aísla las librerías del proyecto para que no se mezclen con otros proyectos de Python que tengas en tu máquina.

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### Windows (CMD)

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

Cuando el entorno esté activo, vas a ver `(venv)` al inicio de la línea de tu terminal. **Recuerda activarlo cada vez que abras una terminal nueva para trabajar en el proyecto.**

Para desactivarlo en cualquier momento: `deactivate`.

---

## 2. Instalar las librerías necesarias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

Si el archivo `requirements.txt` no existe todavía (por ejemplo, si eres la primera persona configurando el proyecto), instala las librerías manualmente y luego genera el archivo para que quede en el repo:

```bash
pip install flask flask-sqlalchemy psycopg2-binary python-dotenv flask-cors
pip freeze > requirements.txt
```

---

## 3. Configurar el archivo `.env`

El repo trae un archivo `.env.example` con las variables necesarias, **sin contraseñas reales**. Cópialo y renómbralo:

```bash
cp .env.example .env
```

Abre `.env` y llena tus propios valores (los de **tu** PostgreSQL local):

```env
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1

DB_USER=postgres
DB_PASSWORD=tu_contraseña_local
DB_HOST=localhost
DB_PORT=5432
DB_NAME=proyecto_bd

DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
si quieres dejar todo por defecto solo cambia DB_USER y DB_PASSWORD
```

⚠️ **El archivo `.env` nunca se sube al repositorio** (ya está en el `.gitignore`). Cada integrante del equipo tiene su propio `.env` con su propia contraseña local de Postgres.

---

## 4. Crear y cargar la base de datos

### 4.1 Crear la base de datos

```bash
# Linux/macOS: puede pedir la contraseña del usuario postgres
createdb -U postgres proyecto_bd
```

Si `createdb` no te funciona directamente, hazlo desde `psql`:

```bash
psql -U postgres
```

```sql
CREATE DATABASE proyecto_bd;
\q
```

### 4.2 Cargar las tablas (DDL)

Con el archivo `.sql` del proyecto (el que tiene todos los `CREATE TABLE`):

```bash
psql -U postgres -d proyecto_bd -f ruta/al/archivo/archivo.sql
```

Si todo corrió bien, no debería salir ningún `ERROR`, solo una lista de `CREATE TABLE`.

### 4.3 Verificar que las tablas quedaron

```bash
psql -U postgres -d proyecto_bd -c "\dt"
```

Deberías ver las tablas: clientes, proveedores, productos, empresa, sedes, pedido, facturas, envios, camion, etc.

---

## 5. Correr el proyecto

Con el entorno virtual activado y el `.env` configurado:

```bash
flask run
```

Si prefieres correrlo directo con Python (si el proyecto tiene un `run.py`):

```bash
python run.py
```

Por defecto debería quedar corriendo en `http://127.0.0.1:5000`.

### Probar que funciona

```bash
curl http://127.0.0.1:5000/api/clientes/
```

Si responde `[]` (una lista vacía) o una lista de clientes, todo está funcionando correctamente.
Tambien se puede probar por medio de POSTMAN (recomendado) usando la url <http://127.0.0.1:5000/api/clientes/> con el metodo GET

---

## 6. Resumen rápido (para cuando ya tengas todo configurado una vez)

Cada vez que vuelvas a trabajar en el proyecto, solo necesitas:

```bash
source venv/bin/activate     # o venv\Scripts\activate en Windows
flask run
```

---

## Problemas comunes

- **`psycopg2` no instala / da error de compilación**: usa `psycopg2-binary` en vez de `psycopg2` (ya está en el `requirements.txt` recomendado arriba).
- **`FATAL: password authentication failed`**: revisa que `DB_PASSWORD` en tu `.env` sea la contraseña real de tu usuario `postgres` local, no la de otro compañero.
- **`could not connect to server`**: verifica que el servicio de PostgreSQL esté corriendo (`sudo systemctl start postgresql` en Linux, o desde los Servicios de Windows / Postgres.app en Mac).
- **Los cambios en el código no se reflejan**: asegúrate de tener `FLASK_DEBUG=1` en el `.env`, así el servidor se reinicia solo al guardar cambios.

## Pruebas en postman

# Guía de pruebas en Postman - Manuelita SAS (simulación)

Base URL local (ajusta el puerto si tu Flask corre en otro):

```
http://localhost:5000
```

⚠️ **Orden recomendado de pruebas** (por las dependencias entre tablas):

1. Empresa y Sedes (si no las tienes precargadas, créalas directo en la BD con SQL, no hay rutas para ellas en este proyecto todavía)
2. Proveedores
3. Tipos de IVA (si no hay ruta, insértalos directo por SQL — son solo 4 valores fijos)
4. Productos (necesitan proveedor + tipo_iva ya creados)
5. Clientes
6. Órdenes a proveedor → recibir orden (esto llena el stock)
7. Camiones y Conductores (con id_sede) — insértalos por SQL si no hay rutas CRUD para ellos aún
8. Pedidos → verificar → confirmar (factura + envío)

---

## 1. Proveedores

### Crear proveedor

`POST /api/proveedores/`

```json
{
  "id_proveedor": "PROV-01",
  "nombre_razon_social": "IMDECO S.A.S",
  "tipo_documento": "NIT",
  "numero_identificacion": "900123456",
  "email": "contacto@imdeco.com",
  "rut": "RUT-900123456",
  "ciudad": "Cali",
  "tipo_proveedor": "materia_prima",
  "tiempo_entrega_promedio": 6,
  "condiciones_pago": 30,
  "calificacion": 4
}
```

### Actualizar proveedor

`PUT /api/proveedores/PROV-01`

```json
{
  "tiempo_entrega_promedio": 4,
  "direccion_operativa": "Calle 10 # 20-30, Cali"
}
```

### Listar / obtener / eliminar

```
GET /api/proveedores/
GET /api/proveedores/PROV-01
DELETE /api/proveedores/PROV-01
```

---

## 2. Productos / Insumos

> Requiere que ya exista `id_proveedor` y `id_tipo_iva`. Los tipos de IVA
> son fijos (general 19%, diferencial 5%, exento/excluido 0%) — créalos
> una sola vez por SQL o agrega una rutita simple de solo-lectura si quieres.

```sql
INSERT INTO TIPOS_IVA (id_tipo_iva, nombre, porcentaje) VALUES
  ('IVA-19', 'General', 19.00),
  ('IVA-5',  'Diferencial', 5.00),
  ('IVA-0',  'Exento', 0.00),
  ('IVA-EXC','Excluido', 0.00);
```

### Crear producto/insumo

`POST /api/productos/`

```json
{
  "id_producto": "PROD-01",
  "id_proveedor": "PROV-01",
  "id_tipo_iva": "IVA-19",
  "nombre": "Resina Epóxica",
  "descripcion": "Resina para recubrimientos industriales",
  "precio": 45000,
  "categoria": "Insumo químico",
  "peso": 5.0,
  "unidad_medida": "kg",
  "inventario_actual": 40,
  "stock_minimo": 15,
  "demanda_diaria": 10
}
```

### Actualizar producto

`PUT /api/productos/PROD-01`

```json
{
  "precio": 47000,
  "demanda_diaria": 12
}
```

### Listar / obtener / lotes / eliminar (lógico)

```
GET /api/productos/
GET /api/productos/PROD-01
GET /api/productos/PROD-01/lotes
DELETE /api/productos/PROD-01
```

---

## 3. Clientes

### Crear cliente

`POST /api/clientes/`

```json
{
  "id_cliente": "CLI-01",
  "tipo_documento": "NIT",
  "numero_identificacion": "800987654",
  "nombre_razon_social": "Distribuciones El Roble SAS",
  "email": "compras@elroble.com",
  "ciudad": "Cali",
  "num_contacto": "3201234567",
  "tipo_num_contacto": "celular"
}
```

### Actualizar cliente

`PUT /api/clientes/CLI-01`

```json
{
  "direccion_residencia": "Cra 15 # 8-20, Cali",
  "num_contacto": "3209998877"
}
```

### Listar / obtener / eliminar

```
GET /api/clientes/
GET /api/clientes/CLI-01
DELETE /api/clientes/CLI-01
```

---

## 4. Órdenes de pedido a proveedor (compra de insumos)

### Crear orden (uno o varios productos)

`POST /api/ordenes/`

```json
{
  "id_orden": "ORD-01",
  "id_sede": "SEDE-01",
  "id_proveedor": "PROV-01",
  "lugar_entrega": "Bodega Central Cali",
  "items": [
    {
      "id_detalle_orden": "DETORD-01",
      "id_producto": "PROD-01",
      "cantidad": 100,
      "costo_unitario": 40000
    }
  ]
}
```

### Recibir la orden (esto genera lotes y sube el stock)

`POST /api/ordenes/ORD-01/recibir`

```json
{
  "dias_para_vencer": 365
}
```

### Listar

```
GET /api/ordenes/
```

---

## 5. Pedidos (venta a cliente)

### Crear pedido

`POST /api/pedidos/`

```json
{
  "id_pedido": "PED-01",
  "id_cliente": "CLI-01",
  "observaciones": "Entrega prioritaria",
  "items": [
    {
      "id_detalle_pedido": "DETPED-01",
      "id_producto": "PROD-01",
      "cantidad_solicitada": 20
    }
  ]
}
```

### Verificar stock del pedido (reserva lotes por FEFO)

`POST /api/pedidos/PED-01/verificar`

```json
{
  "observaciones": "Verificación automática"
}
```

Body vacío `{}` también funciona — el campo es opcional.

### Listar / obtener

```
GET /api/pedidos/
GET /api/pedidos/PED-01
```

---

## 6. Facturas (confirmar pedido verificado → factura + envío)

> El pedido debe estar en estado `verificado` (paso anterior) para poder facturarlo.

### Confirmar pedido y generar factura + envío nacional

`POST /api/facturas/pedidos/PED-01/confirmar`

```json
{
  "id_factura": "FACT-01",
  "numero_factura": "FE-0001",
  "id_empresa": "EMP-01",
  "metodo_pago": "transferencia",
  "envio": {
    "id_envio": "ENV-01",
    "id_sede_origen": "SEDE-01",
    "direccion_origen": "Bodega Central Cali",
    "direccion_destino": "Cra 15 # 8-20, Cali",
    "tipo_envio": "nacional",
    "departamento": "Valle del Cauca",
    "ciudad": "Cali",
    "codigo_postal": "760001",
    "transportadora_local": "Transportes Rápidos SAS"
  }
}
```

### Confirmar pedido y generar factura + envío internacional

`POST /api/facturas/pedidos/PED-02/confirmar`

```json
{
  "id_factura": "FACT-02",
  "numero_factura": "FE-0002",
  "id_empresa": "EMP-01",
  "metodo_pago": "tarjeta",
  "envio": {
    "id_envio": "ENV-02",
    "id_sede_origen": "SEDE-01",
    "direccion_origen": "Bodega Central Cali",
    "direccion_destino": "Miami, FL, USA",
    "tipo_envio": "internacional",
    "pais_destino": "Estados Unidos",
    "aduana": "Aduana Buenaventura",
    "numero_tracking_internacional": "TRK-000123",
    "costo_aduana": 150.5,
    "divisa": "USD"
  }
}
```

### Listar / obtener

```
GET /api/facturas/
GET /api/facturas/FACT-01
```

---

## Errores esperados que deberías poder probar (para validar las reglas de negocio)

| Prueba                                                                  | Resultado esperado                                                                |
| ----------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Crear producto con `id_proveedor` inexistente                           | `400` — "el proveedor no está registrado previamente"                             |
| Eliminar proveedor con productos asociados                              | `409` — "tiene productos/insumos asociados"                                       |
| Eliminar cliente con pedidos asociados                                  | `409` — "tiene pedidos asociados"                                                 |
| Recibir una orden que ya está `recibido`                                | `400` — no se puede recibir dos veces                                             |
| Verificar un pedido pidiendo más cantidad de la que hay en stock        | El pedido queda `rechazado`, `es_valido: false`, con el motivo en `observaciones` |
| Confirmar (facturar) un pedido que sigue en `pendiente` (sin verificar) | `400` — solo se pueden facturar pedidos `verificado`                              |
| Confirmar un envío en una sede sin camiones/conductores disponibles     | `400` — "no hay camiones/conductores disponibles en la sede"                      |
