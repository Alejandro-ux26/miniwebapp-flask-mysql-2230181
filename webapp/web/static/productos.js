const API_PRODUCTOS = '/api/productos';

function mostrarMensaje(texto, tipo) {
    const caja = document.getElementById('mensaje');
    caja.className = 'alert alert-' + tipo;
    caja.textContent = texto;
}

// Llama a la API y lanza un error con el mensaje del servidor si la respuesta no es 2xx
async function pedir(url, opciones) {
    const respuesta = await fetch(url, opciones);
    const datos = await respuesta.json();
    if (!respuesta.ok) {
        throw new Error(datos.error || 'Error ' + respuesta.status);
    }
    return datos;
}

function leerFormulario() {
    return {
        nombre: document.getElementById('nombre').value,
        descripcion: document.getElementById('descripcion').value,
        precio: document.getElementById('precio').value,
        stock: document.getElementById('stock').value
    };
}

function opcionesJson(metodo, cuerpo) {
    return {
        method: metodo,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cuerpo)
    };
}

async function listarProductos() {
    try {
        const productos = await pedir(API_PRODUCTOS);
        const cuerpo = document.querySelector('#tabla-productos tbody');
        cuerpo.innerHTML = '';

        if (productos.length === 0) {
            const fila = cuerpo.insertRow();
            const celda = fila.insertCell();
            celda.colSpan = 5;
            celda.textContent = 'Todavía no hay productos. Crea el primero con el formulario.';
            return;
        }

        productos.forEach(function (p) {
            const fila = document.createElement('tr');
            [p.nombre, p.descripcion || '', p.precio, p.stock].forEach(function (valor) {
                const celda = document.createElement('td');
                celda.textContent = valor;   // textContent evita inyectar HTML
                fila.appendChild(celda);
            });

            const acciones = document.createElement('td');
            const editar = document.createElement('a');
            editar.href = '/productos/' + p.id + '/editar';
            editar.textContent = 'Editar';
            editar.className = 'btn btn-primary btn-sm mr-2';

            const borrar = document.createElement('button');
            borrar.type = 'button';
            borrar.textContent = 'Eliminar';
            borrar.className = 'btn btn-danger btn-sm';
            borrar.addEventListener('click', function () {
                eliminarProducto(p.id, p.nombre);
            });

            acciones.appendChild(editar);
            acciones.appendChild(borrar);
            fila.appendChild(acciones);
            cuerpo.appendChild(fila);
        });
    } catch (error) {
        mostrarMensaje('No se pudo cargar la lista: ' + error.message, 'danger');
    }
}

async function crearProducto(evento) {
    evento.preventDefault();   // evita que el formulario recargue la página
    try {
        await pedir(API_PRODUCTOS, opcionesJson('POST', leerFormulario()));
        document.getElementById('form-producto').reset();
        mostrarMensaje('Producto creado.', 'success');
        listarProductos();
    } catch (error) {
        mostrarMensaje('No se pudo crear el producto: ' + error.message, 'danger');
    }
}

async function eliminarProducto(id, nombre) {
    if (!confirm('¿Eliminar el producto "' + nombre + '"?')) {
        return;
    }
    try {
        await pedir(API_PRODUCTOS + '/' + id, { method: 'DELETE' });
        mostrarMensaje('Producto eliminado.', 'success');
        listarProductos();
    } catch (error) {
        mostrarMensaje('No se pudo eliminar: ' + error.message, 'danger');
    }
}

async function cargarProducto(id) {
    try {
        const p = await pedir(API_PRODUCTOS + '/' + id);
        document.getElementById('nombre').value = p.nombre;
        document.getElementById('descripcion').value = p.descripcion || '';
        document.getElementById('precio').value = p.precio;
        document.getElementById('stock').value = p.stock;
    } catch (error) {
        mostrarMensaje('No se pudo cargar el producto: ' + error.message, 'danger');
    }
}

async function guardarCambios(evento, id) {
    evento.preventDefault();
    try {
        await pedir(API_PRODUCTOS + '/' + id, opcionesJson('PUT', leerFormulario()));
        mostrarMensaje('Cambios guardados.', 'success');
    } catch (error) {
        mostrarMensaje('No se pudieron guardar los cambios: ' + error.message, 'danger');
    }
}
