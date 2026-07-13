/**
 * crud.js
 * Maneja el botón "Eliminar" de cualquier contenedor que tenga el atributo
 * data-api-base (ej. data-api-base="/api/clientes"). Funciona tanto en
 * listas (borra la fila <tr>) como en páginas de detalle (redirige usando
 * data-redirect si no hay fila que borrar).
 *
 * Uso en el HTML (sin necesidad de escribir JS ahí):
 *   <div class="table-responsive" data-api-base="/api/clientes"> ... </div>
 *   <a href="#" class="btn-eliminar" data-id="CLI-01" data-nombre="Acme SAS">Eliminar</a>
 */

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-api-base]").forEach(function (contenedor) {
    const apiBase = contenedor.getAttribute("data-api-base");
    const redireccion = contenedor.getAttribute("data-redirect");

    contenedor.querySelectorAll(".btn-eliminar").forEach(function (boton) {
      boton.addEventListener("click", function (evento) {
        evento.preventDefault();

        const id = boton.getAttribute("data-id");
        const nombre = boton.getAttribute("data-nombre") || id;

        const confirmado = confirm(
          `¿Estás seguro de eliminar "${nombre}"? Esta acción no se puede deshacer.`
        );
        if (!confirmado) {
          return;
        }

        fetch(`${apiBase}/${id}`, { method: "DELETE" })
          .then(function (respuesta) {
            return respuesta.json().then(function (datos) {
              return { ok: respuesta.ok, datos: datos };
            });
          })
          .then(function (resultado) {
            if (!resultado.ok) {
              alert(resultado.datos.error || "No se pudo eliminar el registro.");
              return;
            }

            const fila = boton.closest("tr");
            if (fila) {
              // Estamos en una lista: solo quitamos la fila
              fila.remove();
            } else if (redireccion) {
              // Estamos en una página de detalle: volvemos a la lista
              window.location.href = redireccion;
            } else {
              window.location.reload();
            }
          })
          .catch(function () {
            alert("Error de conexión con el servidor. Intenta de nuevo.");
          });
      });
    });
  });
});
