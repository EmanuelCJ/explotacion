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

@usuario_bp.route('/estado', methods=['GET'])
@jwt_required_cookie()
@require_permiso('ver_usuarios')
def get_usuarios():

    """Listar usuarios sin password no se muestra"""

    data = request.get_json()

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    activo = data.get('activo')
    
    result = UsuarioService.get_estado(page, limit, activo)
    return jsonify(result), 200

@usuario_bp.route('/', methods=['GET'])
@jwt_required_cookie()
@require_permiso('ver_usuarios')
def get_all_usuarios():
    usuarios = UsuarioService.get_all_sin_paginacion()
    return jsonify(usuarios), 200

@usuario_bp.route('/buscar/id', methods=['GET'])
@jwt_required_cookie()
@require_permiso('ver_usuarios')
def get_usuario_id():

    """Obtener usuario por ID"""

    data = request.get_json()

    if not data.get('usuario_id'):
        return jsonify({'error': 'Se requiere usuario_id'}), 400

    try:
        
        usuario_id = int(data.get('usuario_id'))
        usuario = UsuarioService.get_by_id(usuario_id)

        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        return jsonify({'usuario': usuario}), 200
    
    except ValueError:
        return jsonify({'error': 'usuario_id debe ser un número entero'}), 400


@usuario_bp.route('/buscar/username', methods=['GET'])
@jwt_required_cookie()
@require_permiso('ver_usuarios')
def get_usuario_username():

    """Obtener usuario por username"""

    data = request.get_json()

    if not data.get('username'):
        return jsonify({'error': 'Se requiere username'}), 400

    try:
        
        username = data.get('username')
        usuario = UsuarioService.get_username(username)

        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        return jsonify({'usuario': usuario}), 200
    
    except ValueError:
        return jsonify({'error': 'username debe ser una cadena de texto'}), 400


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

@usuario_bp.route('/actualizar', methods=['PUT'])
@jwt_required_cookie()
@require_permiso('editar_usuarios')
def update_usuario():
    """Actualizar usuario"""

    admin_id = get_current_user_id()
    data = request.get_json()

    # Extraer el campo "usuario_id" del JSON y eliminarlo del diccionario de datos
    usuario_id = data.pop('usuario_id', None)

    # Validar que el campo "usuario_id" esté presente en el JSON
    if usuario_id is None:
        return jsonify({'error': 'El campo "usuario_id" es obligatorio'}), 400
    
    # 1. Verifica si el JSON llegó, si tiene contenido y si el ID está presente
    if not data or len(data) == 0:
        return jsonify({'error': 'No se enviaron datos en la solicitud'}), 400
    
    success = UsuarioService.update(usuario_id, data, admin_id)

    if success:
        return jsonify({'message': 'Usuario actualizado correctamente'}), 200
    else:
        return jsonify({'error': 'No se pudo actualizar el usuario'}), 500
    
# No aplica no deberia eliminar un usuario 
# @usuario_bp.route('/eliminar', methods=['DELETE'])
# @jwt_required_cookie()
# @require_permiso('eliminar_usuarios')
# def delete_usuario():
#     """Eliminar usuario"""
#     admin_id = get_current_user_id()
#     data = request.get_json()
#     success = UsuarioService.delete(data['usuario_id'], admin_id)
#     return jsonify({'message': 'Usuario eliminado'}), 200

@usuario_bp.route('/asignar-rol', methods=['POST'])
@jwt_required_cookie()
@require_permiso('asignar_roles')
def asignar_rol():
    """Asignar rol a usuario"""
    admin_id = get_current_user_id()
    data = request.get_json()
    success = UsuarioService.asignar_rol(data['usuario_id'], data['rol_id'], admin_id)

    if success:
        return jsonify({'message': 'Rol asignado'}), 200
    else:
        return jsonify({'error': 'No se pudo asignar el rol'}), 500

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

@usuario_bp.route('/cambiar-password', methods=['POST'])
@jwt_required_cookie()
@require_permiso('editar_usuarios')
def cambiar_password():
    """Cambiar contraseña de un usuario"""

    admin_id = get_current_user_id()
    data = request.get_json()

    success = UsuarioService.cambiar_password(data['usuario_id'], data['new_password'], admin_id)

    if success:
        return jsonify({'message': 'Contraseña actualizada correctamente'}), 200
    else:
        return jsonify({'error': 'No se pudo actualizar la contraseña'}), 500
