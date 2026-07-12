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
