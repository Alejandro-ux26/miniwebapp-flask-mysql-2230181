from decimal import Decimal, InvalidOperation
from flask import Blueprint, request, jsonify
from productos.models.producto_model import Producto
from users.models.db import db

producto_controller = Blueprint('producto_controller', __name__)


def error(mensaje, codigo):
    return jsonify({'error': mensaje}), codigo


def leer_datos(data):
    """Valida el JSON recibido. Devuelve (datos_limpios, mensaje_de_error)."""
    if not isinstance(data, dict):
        return None, 'El cuerpo debe ser un JSON valido'

    nombre = data.get('nombre')
    if not isinstance(nombre, str) or not nombre.strip():
        return None, 'El campo nombre es obligatorio'
    if len(nombre.strip()) > 100:
        return None, 'El nombre no puede superar 100 caracteres'

    descripcion = data.get('descripcion')
    if descripcion is not None:
        if not isinstance(descripcion, str):
            return None, 'La descripcion debe ser texto'
        if len(descripcion) > 255:
            return None, 'La descripcion no puede superar 255 caracteres'

    try:
        precio = Decimal(str(data.get('precio')))
    except InvalidOperation:
        return None, 'El campo precio es obligatorio y debe ser numerico'
    if not precio.is_finite() or precio < 0 or precio > Decimal('99999999.99'):
        return None, 'El precio debe estar entre 0 y 99999999.99'

    try:
        stock = int(data.get('stock', 0))
    except (TypeError, ValueError):
        return None, 'El campo stock debe ser un entero'
    if stock < 0:
        return None, 'El stock no puede ser negativo'

    return {'nombre': nombre.strip(), 'descripcion': descripcion,
            'precio': precio, 'stock': stock}, None


@producto_controller.route('/api/productos', methods=['GET'])
def get_productos():
    print("listado de productos")
    productos = Producto.query.all()
    return jsonify([p.to_dict() for p in productos])


@producto_controller.route('/api/productos/<int:producto_id>', methods=['GET'])
def get_producto(producto_id):
    print("obteniendo producto")
    producto = db.session.get(Producto, producto_id)
    if producto is None:
        return error('Producto no encontrado', 404)
    return jsonify(producto.to_dict())


@producto_controller.route('/api/productos', methods=['POST'])
def create_producto():
    print("creando producto")
    datos, mensaje = leer_datos(request.get_json(silent=True))
    if mensaje:
        return error(mensaje, 400)
    producto = Producto(**datos)
    db.session.add(producto)
    db.session.commit()
    return jsonify(producto.to_dict()), 201


@producto_controller.route('/api/productos/<int:producto_id>', methods=['PUT'])
def update_producto(producto_id):
    print("actualizando producto")
    producto = db.session.get(Producto, producto_id)
    if producto is None:
        return error('Producto no encontrado', 404)
    datos, mensaje = leer_datos(request.get_json(silent=True))
    if mensaje:
        return error(mensaje, 400)
    for campo, valor in datos.items():
        setattr(producto, campo, valor)
    db.session.commit()
    return jsonify(producto.to_dict())


@producto_controller.route('/api/productos/<int:producto_id>', methods=['DELETE'])
def delete_producto(producto_id):
    print("eliminando producto")
    producto = db.session.get(Producto, producto_id)
    if producto is None:
        return error('Producto no encontrado', 404)
    db.session.delete(producto)
    db.session.commit()
    return jsonify({'message': 'Producto eliminado correctamente'})
