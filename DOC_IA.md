# Bitácora de Uso de IA — Análisis y Prompts Sugeridos

**Proyecto:** SGE / Comercializadora "El Valle" S.A.S. (Manuelita SAS)
**Repo revisado:** https://github.com/Atuesta117/Proyecto-Bases-de-Datos-manuelita-SAS-
---

### 1. Fase de Modelado: Generalización ISA para Envíos

**Herramienta utilizada: (Gemini 3.1 Pro)**

**Prompt:**
> "Actúa como DBA experto en modelado relacional. Tengo una tabla ENVIOS con atributos comunes (origen, destino, fechas, estado), pero un envío puede ser 'nacional' (departamento, ciudad, código postal, transportadora local) o 'internacional' (país destino, aduana, tracking, costo aduana, divisa), y estos atributos nunca se solapan. ¿Cómo modelo esto en PostgreSQL con generalización/especialización (ISA) evitando columnas NULL innecesarias?"

**Resultado de la IA:** Propuso ENVIOS como superclase (PK `id_envio`) y dos subclases `ENVIO_NACIONAL` / `ENVIO_INTERNACIONAL`, cada una con `id_envio` como PK y FK hacia ENVIOS con `ON DELETE CASCADE`.

**Ajuste Manual / Validación:** Confirmamos que la especialización es disjunta y total (todo envío es nacional o internacional, nunca ambos ni ninguno). Como Postgres no valida por sí solo que el discriminador `tipo_envio` coincida con la subclase correcta, añadimos esa verificación a nivel de aplicación (Flask) al momento de crear el envío.

---

### 2. Fase de Backend: Reserva de stock por lotes (política FEFO)

**Herramienta utilizada: (Claude Sonnet 5.0)** 

**Prompt:**
> "Necesito una función en Python con SQLAlchemy que, al verificar un pedido, reserve stock siguiendo la política FEFO (el lote que vence primero se despacha primero). Debe recorrer los lotes de un producto ordenados por fecha de vencimiento, descontar lo que ya está comprometido por otros pedidos en estado 'pendiente' o 'verificado', y si no alcanza el stock para algún producto, rechazar el pedido completo sin reservar nada."

**Resultado de la IA:** Entregó una función que recorre lotes ordenados por `fecha_vencimiento` y arma una lista de asignaciones lote-cantidad.

**Ajuste Manual / Validación:** La primera versión de la IA no consideraba que un mismo lote pudiera estar comprometido por pedidos aún no facturados. Añadimos manualmente la subconsulta que resta `cantidad_asignada` de `DetallePedidoLote` para pedidos en estado `pendiente`/`verificado`, evitando que dos pedidos reserven físicamente el mismo stock (sobreventa).

---

### 3. Fase de Backend: Asignación de camión y conductor por sede

**Herramienta utilizada: (Claude Sonnet 5.0)** 

**Prompt:**
> "Escribe una función que, al confirmar un envío, asigne un camión y un conductor disponibles que pertenezcan a la sede de origen del envío. Si no hay camión o conductor disponible en esa sede específica, debe lanzar un error controlado en lugar de asignar uno de otra sede."

**Resultado de la IA:** Generó una función que filtra CAMION y CONDUCTOR por `id_sede` y su estado/disponibilidad.

**Ajuste Manual / Validación:** Agregamos control de "asignación activa" en `CAMION_CONDUCTOR` (`fecha_fin IS NULL`) para no duplicar el vínculo si el camión ya tenía conductor asignado, y añadimos el cambio de estado del camión a `en_ruta` y del conductor a no disponible, como regla de negocio.

---

### 4. Fase de Backend: Restricciones de eliminación (integridad referencial)

**Herramienta utilizada: (Gemini 3.1 Pro)**

**Prompt:**
> "¿Cómo implemento en Flask/SQLAlchemy la regla de que no se pueda eliminar un proveedor si tiene productos u órdenes asociadas, devolviendo un código 409 con un mensaje claro en vez de un error 500 genérico de la base de datos?"

**Resultado de la IA:** Sugirió capturar la excepción `IntegrityError` que lanza PostgreSQL al violar la restricción de FK.

**Ajuste Manual / Validación:** En vez de depender solo del error de la base de datos, agregamos verificaciones explícitas (`tiene_productos_asociados`, `tiene_ordenes_asociadas`) antes del DELETE, para devolver mensajes de negocio claros (409) en lugar de un error crudo de Postgres.

### 5. Fase de Frontend: Vistas HTML y rutas del proyecto

**Herramienta utilizada: (Claude Sonnet 5.0)**

**Prompt:**
> "Créame todas las vistas HTML y las rutas del proyecto (clientes, proveedores, productos, pedidos, órdenes, facturas, envíos), cada una con su listar, ver detalle, crear y cambiar de estado."

**Resultado de la IA:** Generó las vistas y las rutas para todas las entidades del proyecto, cada una con sus endpoints (listar, detalle, crear, cambiar estado) y su archivo de vista para armar los datos que se muestran en las plantillas.

**Ajuste Manual / Validación:** La IA metió parte de la lógica (formatear fechas, traducir el estado) dentro de las rutas en vez de dejarla en el archivo de vistas, rompiendo el orden que ya tenía el proyecto. La movimos al archivo correcto para que las rutas solo reciban la petición y llamen al service/view. También quitó el uso de `render_templates.py`, que ya centralizaba los nombres de plantillas, y lo volvimos a usar.

---


---
