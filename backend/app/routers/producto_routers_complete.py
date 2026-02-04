"""
Router de Productos
CRUD completo de productos con validación de permisos
"""

from flask import Blueprint, request, jsonify
from app.services.producto_service import ProductoService
from app.utils.decoradores_auth import (
    jwt_required_cookie,
    require_permiso,
    get_current_user_id
)


producto_bp = Blueprint('producto', __name__)


@producto_bp.route('/', methods=['GET'])
@jwt_required_cookie()
@require_permiso('ver_productos')
def get_productos():
    """
    Obtener todos los productos con paginación y filtros
    
    Query params:
        - page: Número de página (default: 1)
        - limit: Registros por página (default: 20)
        - categoria_id: Filtrar por categoría
        - activo: Filtrar por estado (true/false)
        - search: Buscar por nombre o código
    
    Returns:
        200: Lista de productos con paginación
    """
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        categoria_id = request.args.get('categoria_id', type=int)
        activo = request.args.get('activo', type=lambda x: x.lower() == 'true')
        search = request.args.get('search', type=str)
        
        result = ProductoService.get_all(
            page=page,
            limit=limit,
            categoria_id=categoria_id,
            activo=activo,
            search=search
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@producto_bp.route('/<int:id>', methods=['GET'])
@jwt_required_cookie()
@require_permiso('ver_productos')
def get_producto(id):
    """
    Obtener un producto por ID con stock detallado
    
    Returns:
        200: Datos del producto con stock por localidad
        404: Producto no encontrado
    """
    try:
        producto = ProductoService.get_by_id(id)
        
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        return jsonify({'producto': producto}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@producto_bp.route('/', methods=['POST'])
@jwt_required_cookie()
@require_permiso('crear_productos')
def create_producto():
    """
    Crear un nuevo producto
    
    Body:
    {
        "nombre": "Cloro Granulado",
        "codigo": "CLORO001",
        "descripcion": "Cloro granulado para tratamiento de agua",
        "id_categoria": 1,
        "costo": 2500.00,
        "unidad_medida": "kg",
        "stock_minimo": 50
    }
    
    Returns:
        201: Producto creado
        400: Datos inválidos
    """
    try:
        usuario_id = get_current_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Crear producto
        producto_id = ProductoService.create(data, usuario_id)
        
        return jsonify({
            'message': 'Producto creado exitosamente',
            'producto_id': producto_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@producto_bp.route('/<int:id>', methods=['PUT'])
@jwt_required_cookie()
@require_permiso('editar_productos')
def update_producto(id):
    """
    Actualizar un producto
    
    Body:
    {
        "nombre": "Nuevo nombre",
        "costo": 3000.00,
        ...
    }
    
    Returns:
        200: Producto actualizado
        404: Producto no encontrado
        400: Datos inválidos
    """
    try:
        usuario_id = get_current_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Actualizar
        success = ProductoService.update(id, data, usuario_id)
        
        if success:
            return jsonify({'message': 'Producto actualizado exitosamente'}), 200
        else:
            return jsonify({'error': 'No se pudo actualizar el producto'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@producto_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required_cookie()
@require_permiso('eliminar_productos')
def delete_producto(id):
    """
    Eliminar (desactivar) un producto
    Solo si no tiene stock
    
    Returns:
        200: Producto eliminado
        400: Tiene stock, no se puede eliminar
        404: Producto no encontrado
    """
    try:
        usuario_id = get_current_user_id()
        
        # Eliminar
        success = ProductoService.delete(id, usuario_id)
        
        if success:
            return jsonify({'message': 'Producto eliminado exitosamente'}), 200
        else:
            return jsonify({'error': 'No se pudo eliminar el producto'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@producto_bp.route('/<int:id>/stock', methods=['GET'])
@jwt_required_cookie()
@require_permiso('ver_productos')
def get_stock_producto(id):
    """
    Obtener stock del producto por localidad/lugar
    
    Returns:
        200: Stock detallado por ubicación
    """
    try:
        stock_por_localidad = ProductoService.get_stock_por_localidad(id)
        
        return jsonify({
            'producto_id': id,
            'stock_por_localidad': stock_por_localidad
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@producto_bp.route('/stock-bajo', methods=['GET'])
@jwt_required_cookie()
@require_permiso('ver_productos')
def get_productos_stock_bajo():
    """
    Obtener productos con stock por debajo del mínimo
    
    Returns:
        200: Lista de productos con stock bajo
    """
    try:
        productos = ProductoService.get_productos_stock_bajo()
        
        return jsonify({
            'count': len(productos),
            'productos': productos
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@producto_bp.route('/<int:id>/verificar-stock', methods=['GET'])
@jwt_required_cookie()
@require_permiso('ver_productos')
def verificar_stock_minimo(id):
    """
    Verificar si un producto está por debajo del stock mínimo
    
    Returns:
        200: Estado del stock
    """
    try:
        resultado = ProductoService.verificar_stock_minimo(id)
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500