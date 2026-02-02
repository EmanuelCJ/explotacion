"""
Router de Movimientos
Maneja entradas, salidas, transferencias y ajustes de stock
CRÍTICO: Actualiza el stock en productos_localidad
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt
from app.services.movimiento_service import MovimientoService
from app.utils.decoradores_auth import (
    jwt_required_custom,
    require_permission,
    require_any_permission,
    get_current_user_id
)


movimiento_bp = Blueprint('movimiento', __name__)


@movimiento_bp.route('/', methods=['GET'])
@jwt_required_custom()
@require_permission('ver_movimientos')
def get_movimientos():
    """
    Obtener todos los movimientos con filtros
    
    Query params:
        - page, limit: Paginación
        - tipo: entrada, salida, transferencia, ajuste
        - producto_id: Filtrar por producto
        - usuario_id: Filtrar por usuario
        - localidad_id: Filtrar por localidad
        - fecha_desde, fecha_hasta: Rango de fechas
    
    Returns:
        200: Lista de movimientos
    """
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        tipo = request.args.get('tipo', type=str)
        producto_id = request.args.get('producto_id', type=int)
        usuario_id = request.args.get('usuario_id', type=int)
        localidad_id = request.args.get('localidad_id', type=int)
        fecha_desde = request.args.get('fecha_desde', type=str)
        fecha_hasta = request.args.get('fecha_hasta', type=str)
        
        result = MovimientoService.get_historial(
            producto_id=producto_id,
            usuario_id=usuario_id,
            localidad_id=localidad_id,
            page=page,
            limit=limit,
            tipo=tipo,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movimiento_bp.route('/<int:id>', methods=['GET'])
@jwt_required_custom()
@require_permission('ver_movimientos')
def get_movimiento(id):
    """
    Obtener un movimiento por ID
    
    Returns:
        200: Datos del movimiento
        404: Movimiento no encontrado
    """
    try:
        movimiento = MovimientoService.get_by_id(id)
        
        if not movimiento:
            return jsonify({'error': 'Movimiento no encontrado'}), 404
        
        return jsonify({'movimiento': movimiento}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movimiento_bp.route('/entrada', methods=['POST'])
@jwt_required_custom()
@require_permission('registrar_entrada')
def crear_entrada():
    """
    Registrar entrada de stock
    SUMA stock al lugar de destino
    
    Body:
    {
        "id_producto": 1,
        "cantidad": 50,
        "lugar_destino": 1,
        "motivo": "Compra a proveedor",
        "observaciones": "Factura #123"
    }
    
    Returns:
        201: Movimiento creado y stock actualizado
        400: Datos inválidos
    """
    try:
        usuario_id = get_current_user_id()
        claims = get_jwt()
        localidad_id = claims.get('localidad_id')
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Crear entrada
        movimiento_id = MovimientoService.crear_entrada(data, usuario_id, localidad_id)
        
        return jsonify({
            'message': 'Entrada registrada exitosamente',
            'movimiento_id': movimiento_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@movimiento_bp.route('/salida', methods=['POST'])
@jwt_required_custom()
@require_permission('registrar_salida')
def crear_salida():
    """
    Registrar salida de stock
    RESTA stock del lugar de origen
    Valida que haya stock suficiente
    
    Body:
    {
        "id_producto": 1,
        "cantidad": 20,
        "lugar_origen": 1,
        "motivo": "Uso en obra",
        "observaciones": "Obra Barrio Norte"
    }
    
    Returns:
        201: Movimiento creado y stock actualizado
        400: Stock insuficiente o datos inválidos
    """
    try:
        usuario_id = get_current_user_id()
        claims = get_jwt()
        localidad_id = claims.get('localidad_id')
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Crear salida
        movimiento_id = MovimientoService.crear_salida(data, usuario_id, localidad_id)
        
        return jsonify({
            'message': 'Salida registrada exitosamente',
            'movimiento_id': movimiento_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@movimiento_bp.route('/transferencia', methods=['POST'])
@jwt_required_custom()
@require_permission('registrar_transferencia')
def crear_transferencia():
    """
    Transferir stock entre lugares
    RESTA del origen y SUMA al destino
    
    Body:
    {
        "id_producto": 1,
        "cantidad": 15,
        "lugar_origen": 1,
        "lugar_destino": 2,
        "motivo": "Reubicación",
        "observaciones": ""
    }
    
    Returns:
        201: Transferencia realizada
        400: Stock insuficiente o datos inválidos
    """
    try:
        usuario_id = get_current_user_id()
        claims = get_jwt()
        localidad_id = claims.get('localidad_id')
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Crear transferencia
        movimiento_id = MovimientoService.crear_transferencia(data, usuario_id, localidad_id)
        
        return jsonify({
            'message': 'Transferencia realizada exitosamente',
            'movimiento_id': movimiento_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@movimiento_bp.route('/ajuste', methods=['POST'])
@jwt_required_custom()
@require_permission('registrar_ajuste')
def crear_ajuste():
    """
    Ajustar stock (inventario físico)
    Establece el stock a una cantidad específica
    
    Body:
    {
        "id_producto": 1,
        "lugar_id": 1,
        "cantidad_nueva": 100,
        "motivo": "Inventario físico mensual",
        "observaciones": "Realizado por equipo de almacén"
    }
    
    Returns:
        201: Ajuste realizado
        400: Datos inválidos
    """
    try:
        usuario_id = get_current_user_id()
        claims = get_jwt()
        localidad_id = claims.get('localidad_id')
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Crear ajuste
        movimiento_id = MovimientoService.crear_ajuste(data, usuario_id, localidad_id)
        
        return jsonify({
            'message': 'Ajuste de inventario realizado exitosamente',
            'movimiento_id': movimiento_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@movimiento_bp.route('/ultimos', methods=['GET'])
@jwt_required_custom()
@require_permission('ver_movimientos')
def get_ultimos_movimientos():
    """
    Obtener los últimos N movimientos
    
    Query params:
        - limit: Cantidad de movimientos (default: 10)
    
    Returns:
        200: Lista de últimos movimientos
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        movimientos = MovimientoService.get_ultimos(limit)
        
        return jsonify({
            'count': len(movimientos),
            'movimientos': movimientos
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500