"""Router de Auditoría - Solo Maestro y Supervisor"""

from flask import Blueprint, request, jsonify
from app.services import AuditoriaService
from app.utils.decoradores_auth import jwt_required_custom, require_permission

auditoria_bp = Blueprint('auditoria', __name__)

@auditoria_bp.route('/', methods=['GET'])
@jwt_required_custom()
@require_permission('ver_auditoria')
def get_auditoria():
    """Obtener auditoría con filtros"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    entidad = request.args.get('entidad', type=str)
    accion = request.args.get('accion', type=str)
    usuario_id = request.args.get('usuario_id', type=int)
    
    result = AuditoriaService.get_all(
        page=page,
        limit=limit,
        entidad=entidad,
        accion=accion,
        usuario_id=usuario_id
    )
    
    return jsonify(result), 200

@auditoria_bp.route('/usuario/<int:usuario_id>', methods=['GET'])
@jwt_required_custom()
@require_permission('ver_auditoria_usuario')
def get_auditoria_usuario(usuario_id):
    """Ver qué hizo un usuario específico"""
    page = request.args.get('page', 1, type=int)
    result = AuditoriaService.get_by_usuario(usuario_id, page)
    return jsonify(result), 200

@auditoria_bp.route('/estadisticas', methods=['GET'])
@jwt_required_custom()
@require_permission('ver_auditoria')
def get_estadisticas():
    """Estadísticas de auditoría"""
    stats = AuditoriaService.get_estadisticas()
    return jsonify(stats), 200