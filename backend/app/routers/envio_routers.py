"""
Router de Envíos
Maneja envíos de productos entre localidades
"""

from flask import Blueprint, request, jsonify
from app.services.envio_service import EnvioService
from app.utils.decoradores_auth import (
    jwt_required_custom,
    require_permission,
    get_current_user_id
)


envio_bp = Blueprint('envio', __name__)


@envio_bp.route('/', methods=['GET'])
@jwt_required_custom()
@require_permission('ver_envios')
def get_envios():
    """
    Obtener todos los envíos con filtros
    
    Query params:
        - page, limit: Paginación
        - estado: enviado, en_transito, recibido, cancelado
        - localidad_origen, localidad_destino: Filtrar por localidades
        - producto_id: Filtrar por producto
    
    Returns:
        200: Lista de envíos
    """
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        estado = request.args.get('estado', type=str)
        localidad_origen = request.args.get('localidad_origen', type=int)
        localidad_destino = request.args.get('localidad_destino', type=int)
        producto_id = request.args.get('producto_id', type=int)
        
        result = EnvioService.get_all(
            page=page,
            limit=limit,
            estado=estado,
            localidad_origen=localidad_origen,
            localidad_destino=localidad_destino,
            producto_id=producto_id
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@envio_bp.route('/<int:id>', methods=['GET'])
@jwt_required_custom()
@require_permission('ver_envios')
def get_envio(id):
    """
    Obtener un envío por ID
    
    Returns:
        200: Datos del envío
        404: Envío no encontrado
    """
    try:
        envio = EnvioService.get_by_id(id)
        
        if not envio:
            return jsonify({'error': 'Envío no encontrado'}), 404
        
        return jsonify({'envio': envio}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@envio_bp.route('/', methods=['POST'])
@jwt_required_custom()
@require_permission('enviar_productos')
def crear_envio():
    """
    Crear un nuevo envío
    RESTA el stock del lugar de origen
    
    Body:
    {
        "id_producto": 1,
        "cantidad": 30,
        "localidad_destino": 2,
        "lugar_origen": 1,
        "lugar_destino": 5,  (opcional)
        "motivo": "Reposición Bariloche",
        "observaciones_envio": "Envío urgente"
    }
    
    Returns:
        201: Envío creado y stock descontado
        400: Stock insuficiente o datos inválidos
    """
    try:
        usuario_envia_id = get_current_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Crear envío
        envio_id = EnvioService.crear_envio(data, usuario_envia_id)
        
        return jsonify({
            'message': 'Envío creado exitosamente',
            'envio_id': envio_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@envio_bp.route('/<int:id>/recibir', methods=['POST'])
@jwt_required_custom()
@require_permission('recibir_productos')
def recibir_envio(id):
    """
    Marcar un envío como recibido
    SUMA el stock al lugar de destino
    
    Body:
    {
        "lugar_destino_id": 5,
        "observaciones": "Recibido en buen estado"
    }
    
    Returns:
        200: Envío recibido y stock actualizado
        400: Envío ya recibido o cancelado
    """
    try:
        usuario_recibe_id = get_current_user_id()
        data = request.get_json()
        
        if not data or 'lugar_destino_id' not in data:
            return jsonify({'error': 'lugar_destino_id es requerido'}), 400
        
        # Recibir envío
        success = EnvioService.recibir_envio(
            id,
            usuario_recibe_id,
            data['lugar_destino_id'],
            data.get('observaciones', '')
        )
        
        if success:
            return jsonify({'message': 'Envío recibido exitosamente'}), 200
        else:
            return jsonify({'error': 'No se pudo recibir el envío'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@envio_bp.route('/<int:id>/cancelar', methods=['POST'])
@jwt_required_custom()
@require_permission('cancelar_envios')
def cancelar_envio(id):
    """
    Cancelar un envío
    DEVUELVE el stock al lugar de origen
    
    Body:
    {
        "observaciones": "Cancelado por error en cantidad"
    }
    
    Returns:
        200: Envío cancelado y stock devuelto
        400: Envío ya recibido (no se puede cancelar)
    """
    try:
        usuario_id = get_current_user_id()
        data = request.get_json()
        
        observaciones = data.get('observaciones', '') if data else ''
        
        # Cancelar envío
        success = EnvioService.cancelar_envio(id, usuario_id, observaciones)
        
        if success:
            return jsonify({'message': 'Envío cancelado exitosamente'}), 200
        else:
            return jsonify({'error': 'No se pudo cancelar el envío'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@envio_bp.route('/pendientes', methods=['GET'])
@jwt_required_custom()
@require_permission('recibir_productos')
def get_pendientes_recepcion():
    """
    Obtener envíos pendientes de recibir en mi localidad
    
    Query params:
        - localidad_id: ID de la localidad (requerido)
    
    Returns:
        200: Lista de envíos pendientes
    """
    try:
        localidad_id = request.args.get('localidad_id', type=int)
        
        if not localidad_id:
            return jsonify({'error': 'localidad_id es requerido'}), 400
        
        envios = EnvioService.get_pendientes_recepcion(localidad_id)
        
        return jsonify({
            'count': len(envios),
            'envios': envios
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@envio_bp.route('/mis-envios', methods=['GET'])
@jwt_required_custom()
@require_permission('ver_envios')
def get_mis_envios():
    """
    Obtener envíos realizados por mí
    
    Returns:
        200: Lista de envíos que yo hice
    """
    try:
        usuario_id = get_current_user_id()
        
        envios = EnvioService.get_mis_envios(usuario_id)
        
        return jsonify({
            'count': len(envios),
            'envios': envios
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@envio_bp.route('/mis-recepciones', methods=['GET'])
@jwt_required_custom()
@require_permission('ver_envios')
def get_mis_recepciones():
    """
    Obtener envíos que yo he recibido
    
    Returns:
        200: Lista de envíos que yo recibí
    """
    try:
        usuario_id = get_current_user_id()
        
        envios = EnvioService.get_mis_recepciones(usuario_id)
        
        return jsonify({
            'count': len(envios),
            'envios': envios
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500