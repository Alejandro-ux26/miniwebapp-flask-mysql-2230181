from flask import Flask, render_template
from users.controllers.user_controller import user_controller
from users.models.db import db
from productos.controllers.producto_controller import producto_controller

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)

# Registrando los blueprints de las APIs (usuarios y productos)
app.register_blueprint(user_controller)
app.register_blueprint(producto_controller)

# Ruta para renderizar el template index.html
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/edit/<string:id>')
def edit_user(id):
    print("id recibido",id)
    return render_template('edit.html', id=id)

# Paginas de gestion de productos
@app.route('/productos')
def productos():
    return render_template('productos.html')

@app.route('/productos/<int:id>/editar')
def editar_producto(id):
    return render_template('editar_producto.html', id=id)

if __name__ == '__main__':
    app.run()
