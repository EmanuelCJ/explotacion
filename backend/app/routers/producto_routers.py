from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.producto_service import ProductoService
from app.services.movimiento_service import MovimientoService
from app.services.auditoria_service import AuditoriaService
from app.utils.validation_rol import require_role

producto_bp = Blueprint('producto', __name__)
producto_service = ProductoService()
movimiento_service = MovimientoService()
auditoria_service = AuditoriaService()

@producto_bp.route('/', methods=['GET'])
@jwt_required()
def get_productos():
    """
    Obtener todos los productos con paginación
    Query params: ?page=1&limit=20&categoria_id=1&activo=true&search=nombre
    """
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        categoria_id = request.args.get('categoria_id', type=int)
        activo = request.args.get('activo', type=lambda x: x.lower() == 'true')
        search = request.args.get('search', type=str)
        
        result = producto_service.get_all(
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
@jwt_required()
def get_producto(id):
    """Obtener un producto por ID"""
    try:
        producto = producto_service.get_by_id(id)
        
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        return jsonify({'producto': producto}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@producto_bp.route('/', methods=['POST'])
@jwt_required()
@require_role(['admin', 'gestor'])
def create_producto():
    """
    Crear un nuevo producto
    Body: {
        "nombre": "Producto A",
        "descripcion": "Descripción del producto",
        "codigo": "PROD001",
        "categoria_id": 1,
        "stock_minimo": 10,
        "stock_maximo": 100,
        "precio": 50.00,
        "activo": true
    }
    """
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Validaciones
        required_fields = ['nombre', 'codigo', 'categoria_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        # Crear producto
        producto_id = producto_service.create(data)
        
        # Registrar auditoría
        auditoria_service.registrar(
            usuario_id=current_user,
            accion='CREATE',
            tabla='productos',
            registro_id=producto_id,
            descripcion=f"Producto creado: {data['nombre']}"
        )
        
        return jsonify({
            'message': 'Producto creado exitosamente',
            'producto_id': producto_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@producto_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@require_role(['admin', 'gestor'])
def update_producto(id):
    """
    Actualizar un producto
    Body: {
        "nombre": "Producto A Actualizado",
        "descripcion": "Nueva descripción",
        "precio": 55.00
    }
    """
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Verificar que existe
        producto = producto_service.get_by_id(id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Actualizar
        producto_service.update(id, data)
        
        # Registrar auditoría
        auditoria_service.registrar(
            usuario_id=current_user,
            accion='UPDATE',
            tabla='productos',
            registro_id=id,
            descripcion=f"Producto actualizado: {data.get('nombre', producto['nombre'])}"
        )
        
        return jsonify({'message': 'Producto actualizado exitosamente'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@producto_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@require_role(['admin'])
def delete_producto(id):
    """Eliminar (soft delete) un producto"""
    try:
        current_user = get_jwt_identity()
        
        # Verificar que existe
        producto = producto_service.get_by_id(id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Soft delete
        producto_service.delete(id)
        
        # Registrar auditoría
        auditoria_service.registrar(
            usuario_id=current_user,
            accion='DELETE',
            tabla='productos',
            registro_id=id,
            descripcion=f"Producto eliminado: {producto['nombre']}"
        )
        
        return jsonify({'message': 'Producto eliminado exitosamente'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@producto_bp.route('/<int:id>/stock', methods=['GET'])
@jwt_required()
def get_stock_by_lugar(id):
    """
    Obtener stock del producto por lugar
    """
    try:
        stock_lugares = producto_service.get_stock_por_lugar(id)
        
        return jsonify({
            'producto_id': id,
            'stock_por_lugar': stock_lugares
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@producto_bp.route('/<int:id>/movimiento', methods=['POST'])
@jwt_required()
@require_role(['admin', 'gestor', 'operador'])
def crear_movimiento_producto(id):
    """
    Crear un movimiento de producto (entrada/salida)
    Body: {
        "tipo": "entrada|salida|transferencia",
        "cantidad": 10,
        "lugar_origen_id": 1,
        "lugar_destino_id": 2,
        "motivo": "Compra de mercadería",
        "observaciones": "Opcional"
    }
    """
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Validaciones
        required_fields = ['tipo', 'cantidad']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        tipo = data.get('tipo')
        if tipo not in ['entrada', 'salida', 'transferencia']:
            return jsonify({'error': 'Tipo debe ser: entrada, salida o transferencia'}), 400
        
        if tipo in ['salida', 'transferencia'] and 'lugar_origen_id' not in data:
            return jsonify({'error': 'lugar_origen_id es requerido para salida/transferencia'}), 400
        
        if tipo in ['entrada', 'transferencia'] and 'lugar_destino_id' not in data:
            return jsonify({'error': 'lugar_destino_id es requerido para entrada/transferencia'}), 400
        
        # Crear movimiento
        movimiento_id = movimiento_service.crear_movimiento(
            producto_id=id,
            usuario_id=current_user,
            tipo=tipo,
            cantidad=data['cantidad'],
            lugar_origen_id=data.get('lugar_origen_id'),
            lugar_destino_id=data.get('lugar_destino_id'),
            motivo=data.get('motivo', ''),
            observaciones=data.get('observaciones', '')
        )
        
        # Registrar auditoría
        auditoria_service.registrar(
            usuario_id=current_user,
            accion='MOVIMIENTO',
            tabla='movimientos',
            registro_id=movimiento_id,
            descripcion=f"Movimiento {tipo}: {data['cantidad']} unidades del producto {id}"
        )
        
        return jsonify({
            'message': 'Movimiento registrado exitosamente',
            'movimiento_id': movimiento_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@producto_bp.route('/<int:id>/historial', methods=['GET'])
@jwt_required()
def get_historial_producto(id):
    """
    Obtener historial de movimientos de un producto
    Query params: ?page=1&limit=20&tipo=entrada
    """
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        tipo = request.args.get('tipo', type=str)
        
        historial = movimiento_service.get_historial_producto(
            producto_id=id,
            page=page,
            limit=limit,
            tipo=tipo
        )
        
        return jsonify(historial), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500