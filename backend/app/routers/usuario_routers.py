"""Router de Usuarios - Solo para Admin"""

from flask import Blueprint, request, jsonify
from app.services.usuario_service import UsuarioService
from app.utils.decoradores_auth import (
    jwt_required_cookie,
    require_permiso,
    get_current_user_id,
    require_role
)

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/', methods=['GET'])
@jwt_required_cookie()
@require_permiso('ver_usuarios')
def get_usuarios():
    """Listar usuarios"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    activo = request.args.get('activo', type=lambda x: x.lower() == 'true')
    
    result = UsuarioService.get_all(page, limit, activo)
    return jsonify(result), 200

@usuario_bp.route('/<int:id>', methods=['GET'])
@jwt_required_cookie()
@require_permiso('ver_usuarios')
def get_usuario(id):
    """Obtener usuario por ID"""
    usuario = UsuarioService.get_by_id(id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({'usuario': usuario}), 200

@usuario_bp.route('/create', methods=['POST'])
@jwt_required_cookie()
@require_permiso('crear_usuarios')
@require_role('admin')
def create_usuario():
    """
    Crear nuevo usuario
    {
     "nombre" : "adminTest",
     "apellido" : "test",
     "username" : "subadmin",
     "email" : "ejemplo@gmail.com",
     "password" : "arsa2026",
     "legajo" : "9999",
     "id_localidad" : 1,
     "id_rol" : 2
    }
    
    """
    
    admin_id = get_current_user_id()
    data = request.get_json()
    
    usuario_id = UsuarioService.create(data, admin_id)
    return jsonify({
        'success': True,
        'message': 'Usuario creado',
        'usuario_id': usuario_id
    }), 201

@usuario_bp.route('/<int:id>', methods=['PUT'])
@jwt_required_cookie()
@require_permiso('editar_usuarios')
def update_usuario(id):
    """Actualizar usuario"""
    admin_id = get_current_user_id()
    data = request.get_json()
    
    success = UsuarioService.update(id, data, admin_id)
    return jsonify({'message': 'Usuario actualizado'}), 200

@usuario_bp.route('/eliminar', methods=['DELETE'])
@jwt_required_cookie()
@require_permiso('eliminar_usuarios')
def delete_usuario():
    """Eliminar usuario"""
    admin_id = get_current_user_id()
    data = request.get_json()
    success = UsuarioService.delete(data['usuario_id'], admin_id)
    return jsonify({'message': 'Usuario eliminado'}), 200

@usuario_bp.route('/asignar-rol', methods=['POST'])
@jwt_required_cookie()
@require_permiso('asignar_roles')
def asignar_rol():
    """Asignar rol a usuario"""
    admin_id = get_current_user_id()
    data = request.get_json()
    success = UsuarioService.asignar_rol(data['usuario_id'], data['rol_id'], admin_id)
    return jsonify({'message': 'Rol asignado'}), 200

#se rol_id por que no era necesario, cada usuario debe tener un rol asignado
@usuario_bp.route('/quitar-rol', methods=['POST'])
@jwt_required_cookie()
@require_permiso('asignar_roles')
def remover_rol():
    """Remover rol de usuario"""
    admin_id = get_current_user_id()
    data = request.get_json()  
    success = UsuarioService.quitar_rol(data['usuario_id'], admin_id)
    return jsonify({'message': 'Rol removido'}), 200

@usuario_bp.route('/activar', methods=['POST'])
@jwt_required_cookie()
@require_permiso('editar_usuarios')
def activar_usuario():
    """Activar usuario"""
    admin_id = get_current_user_id()
    data = request.get_json()
    success = UsuarioService.activar_usuario(data['usuario_id'], admin_id)
    return jsonify({'message': 'Usuario activado'}), 200

@usuario_bp.route('/desactivar', methods=['POST'])
@jwt_required_cookie()
@require_permiso('editar_usuarios')
def desactivar_usuario():
    """Desactivar usuario"""
    admin_id = get_current_user_id()
    data = request.get_json()
    success = UsuarioService.desactivar_usuario(data['usuario_id'], admin_id)
    return jsonify({'message': 'Usuario desactivado'}), 200

