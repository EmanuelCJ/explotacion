"""Router de Usuarios - Solo para Admin"""

from flask import Blueprint, request, jsonify
from app.services.usuario_service import UsuarioService
from app.utils.decoradores_auth import (
    jwt_required_custom,
    require_permission,
    get_current_user_id
)

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/', methods=['GET'])
@jwt_required_custom()
@require_permission('ver_usuarios')
def get_usuarios():
    """Listar usuarios"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    activo = request.args.get('activo', type=lambda x: x.lower() == 'true')
    
    result = UsuarioService.get_all(page, limit, activo)
    return jsonify(result), 200

@usuario_bp.route('/<int:id>', methods=['GET'])
@jwt_required_custom()
@require_permission('ver_usuarios')
def get_usuario(id):
    """Obtener usuario por ID"""
    usuario = UsuarioService.get_by_id(id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({'usuario': usuario}), 200

@usuario_bp.route('/', methods=['POST'])
@jwt_required_custom()
@require_permission('crear_usuarios')
def create_usuario():
    """Crear usuario (solo admin)"""
    admin_id = get_current_user_id()
    data = request.get_json()
    
    usuario_id = UsuarioService.create(data, admin_id)
    return jsonify({
        'message': 'Usuario creado',
        'usuario_id': usuario_id
    }), 201

@usuario_bp.route('/<int:id>', methods=['PUT'])
@jwt_required_custom()
@require_permission('editar_usuarios')
def update_usuario(id):
    """Actualizar usuario"""
    admin_id = get_current_user_id()
    data = request.get_json()
    
    success = UsuarioService.update(id, data, admin_id)
    return jsonify({'message': 'Usuario actualizado'}), 200

@usuario_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required_custom()
@require_permission('eliminar_usuarios')
def delete_usuario(id):
    """Eliminar usuario"""
    admin_id = get_current_user_id()
    success = UsuarioService.delete(id, admin_id)
    return jsonify({'message': 'Usuario eliminado'}), 200

@usuario_bp.route('/<int:usuario_id>/rol/<int:rol_id>', methods=['POST'])
@jwt_required_custom()
@require_permission('asignar_roles')
def asignar_rol(usuario_id, rol_id):
    """Asignar rol a usuario"""
    admin_id = get_current_user_id()
    success = UsuarioService.asignar_rol(usuario_id, rol_id, admin_id)
    return jsonify({'message': 'Rol asignado'}), 200