# Práctica Flask + REST + MySQL

Universidad Autónoma de Occidente, Facultad de Ingeniería. Materia: Servicios Telemáticos.

- **Estudiante:** Jose Alejandro Castillo Arce
- **Código:** 2230181
- **GitHub:** Alejandro-ux26
- **Base del proyecto:** https://github.com/omondragon/MiniWebApp (aplicación de ejemplo del profesor)

**Objetivo:** construir una aplicación web y una API REST en Python Flask con persistencia de datos en MySQL, sobre una máquina virtual Ubuntu en Vagrant, y desplegarla en Apache.

## Estructura del repositorio

```
.
├── Vagrantfile            VM servidorWeb (192.168.60.3)
├── script.sh              Aprovisionamiento: MySQL, Flask y dependencias
├── init.sql               Base myflaskapp: tablas users y productos
├── productos.sql          Script de la tabla productos (ya incluido en init.sql)
├── miniwebapp.conf        VirtualHost de Apache (punto 6)
├── webapp/
│   ├── run.py, config.py
│   ├── application.wsgi   Punto de entrada para mod_wsgi
│   ├── users/             API de usuarios (original del profesor)
│   ├── productos/         API de productos (punto 5)
│   └── web/               Rutas de las páginas, templates y JavaScript
└── evidencias/            Capturas de cada punto
```

## Cómo ejecutarla

```powershell
vagrant up
vagrant ssh servidorWeb
```

**Modo desarrollo (Flask):**

```bash
cd /vagrant/webapp
export FLASK_APP=run.py
python3 -m flask run --host=0.0.0.0 --debug
```

Abrir `http://192.168.60.3:5000`.

**Modo producción (Apache):** ver el punto 6. Abrir `http://192.168.60.3`.

## Cambios respecto al repositorio original

| Cambio | Motivo |
|---|---|
| Box `ubuntu/jammy64` en lugar de `bento/ubuntu-22.04` | Con el box original la VM arrancaba bien la primera vez, pero tras un `vagrant halt` el SSH no respondía (timeout). Con `ubuntu/jammy64` el ciclo halt y up funciona. |
| API y páginas de productos (`webapp/productos`, `productos.html`, `editar_producto.html`, `productos.js`) | Punto 5. |
| `views.py` con los blueprints y rutas nuevas | Registrar la API de productos y sus páginas. |
| `application.wsgi` y `miniwebapp.conf` | Punto 6. |
| `init.sql` con la tabla `productos` | Que una VM nueva quede con ambas tablas. |

## Desarrollo por punto

### Ejercicio 1: base de datos en MySQL

```bash
systemctl status mysql
mysql -u root -proot
```

```sql
use myflaskapp;
show tables;
describe users;
select * from users;
```

Resultado: MySQL 8.0 activo, base `myflaskapp` con la tabla `users` (5 columnas, `id` clave primaria con `auto_increment`) y 2 filas iniciales (`juan` y `maria`).
Evidencia: `evidencias/01_ej1_mysql.png`

### Punto 2: código de la aplicación

| Archivo | Rol |
|---|---|
| `run.py` | Punto de entrada: importa `app` de `web.views`. |
| `web/views.py` | Crea la app, carga la configuración, registra los blueprints y sirve las páginas HTML. |
| `users/controllers/user_controller.py` | API REST de usuarios (`/api/users`). |
| `users/models/user_model.py` | Modelo `Users` (ORM SQLAlchemy mapeado a la tabla `users`). |
| `config.py` | Conexión: `mysql://root:root@localhost/myflaskapp`. |
| `web/static/script.js` | Cliente: llama a la API con `fetch` y dibuja la tabla. |

La página web y la API son lo mismo: los templates casi no traen datos, el navegador los pide a `/api/users` con JavaScript.

**Recorrido de una petición (botón "Get Users"):**

```
onclick="getUsers()"  ->  fetch('/api/users')  ->  ruta GET /api/users (get_users)
  ->  Users.query.all()  ->  SELECT ... FROM users  ->  MySQL devuelve las filas
  ->  jsonify([...]) sin el campo password  ->  script.js crea las filas <tr>
```

**Prueba de la web:** se creó, editó y eliminó un usuario desde el navegador, y en cada paso el log de Flask mostró la petición (`POST 201`, `PUT 200`, `DELETE 200`) y `select * from users` confirmó el cambio en MySQL.
Evidencias: `evidencias/02_web_usuarios.png`, `evidencias/03_log_flask_usuarios.png`

**Hallazgos del análisis:**

| Hallazgo | Evidencia | Cómo se trató |
|---|---|---|
| El GET no devuelve `password`, pero `edit.html` la asigna al campo: queda `undefined` y al guardar se escribe ese texto. | La contraseña de un usuario de prueba pasó de `789` a `undefined`. | No se corrigió en `users`. |
| El botón de guardar es `submit`: recarga la página y compite con el `PUT`. | En el log, `GET /edit/3` y `PUT /api/users/3` aparecen en el mismo segundo. | Los templates de productos usan `preventDefault()`. |
| Un POST incompleto responde `500` en lugar de `400`. | `curl` con `{"name":"x"}` devolvió `500` (`KeyError`). | La API de productos valida y responde `400`. |
| Los errores `404` y `500` se devuelven como HTML, no como JSON. | Respuestas de `curl` y Postman. | La API de productos responde JSON. |
| Las contraseñas se guardan en texto plano. | `select * from users` muestra `123` y `456`. | Fuera del alcance de la práctica. |
| El modelo (`String(100)`, `unique=True`) no coincide con la tabla real (`varchar(255)`, sin `UNIQUE`). | Comparar `user_model.py` con `init.sql`. | El modelo de productos coincide con su tabla. |

### Punto 3: pruebas de la API REST

**a) curl** (dentro de la VM):

| Operación | Código |
|---|---|
| `GET /api/users` y `GET /api/users/1` | `200` |
| `POST /api/users` | `201` |
| `PUT /api/users/4` | `200` |
| `DELETE /api/users/4` | `200` |
| `GET /api/users/4` (ya borrado) | `404` |
| `POST` con cuerpo incompleto | `500` |

El usuario creado recibió el id 4 y no el 3: MySQL no reutiliza los ids de filas borradas.
Evidencia: `evidencias/04_curl_usuarios.png`

**b) Postman:** colección `MiniWebApp Users` con 8 peticiones y la variable de entorno `base_url` (`http://192.168.60.3:5000`). Los códigos fueron los mismos que con curl (el id nuevo fue el 5).
Evidencia: `evidencias/05_postman_usuarios.png`

### Punto 4: ¿qué sucede con los datos al apagar la máquina?

| Acción | Resultado |
|---|---|
| `vagrant halt` y `vagrant up` | El usuario creado antes del apagado sigue en la tabla. |
| `vagrant destroy` y `vagrant up` | Solo reaparecen `juan` y `maria`: el usuario se perdió. |
| Restaurar un respaldo hecho con `mysqldump` | El usuario vuelve con su mismo id. |

Los datos persisten porque MySQL los guarda en archivos dentro del disco virtual de la VM (`/var/lib/mysql`), no en la memoria de la aplicación. `vagrant halt` apaga el sistema pero conserva ese disco; `vagrant destroy` lo elimina, y la VM se recrea desde cero con los datos de `init.sql`. Para conservar datos se hizo un respaldo en la carpeta compartida con Windows (`/vagrant`), que sobrevive a la destrucción de la VM:

```bash
mysqldump -u root -proot myflaskapp > /vagrant/respaldo_myflaskapp.sql
mysql -u root -proot myflaskapp < /vagrant/respaldo_myflaskapp.sql
```

(El archivo de respaldo no se sube al repositorio porque contiene contraseñas.)

Flask, lanzado a mano, no se reinició tras el apagado (`Connection refused`), mientras que MySQL sí, por ser un servicio de systemd habilitado. Esto contrasta con la API de libros de la práctica anterior, cuyos datos vivían en memoria y se perdían al reiniciar el proceso.
Evidencias: `evidencias/06_persistencia_antes.png`, `evidencias/07_persistencia_halt.png`, `evidencias/08_persistencia_destroy.png`, `evidencias/09_persistencia_restaurar.png`