"""
Decoradores de Autenticación y Autorización
Validan JWT desde cookies HttpOnly y permisos de usuarios
"""

from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.services.auth_service import AuthService


def jwt_required_cookie():
    """
    Decorador personalizado que valida JWT desde cookie HttpOnly
    
    Usage:
        @router.route('/endpoint')
        @jwt_required_custom()
        def mi_endpoint():
            usuario_id = get_jwt_identity()
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # Verificar JWT (automáticamente lo busca en la cookie)
                verify_jwt_in_request()
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'Token invalido o expirado',
                    'detail': str(e)
                }), 401
        return wrapper
    return decorator


def require_permiso(permiso_name: str):
    """
    Decorador para validar que el usuario tenga un permiso específico
    
    Args:
        permiso_name: Nombre del permiso requerido
    
    Usage:
        @router.route('/productos', methods=['POST'])
        @jwt_required_custom()
        @require_permiso('crear_productos')
        def crear_producto():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # Obtener usuario del JWT
                usuario_id = get_jwt_identity()
                
                # Validar permiso
                tiene_permiso = AuthService.validate_permissions(usuario_id, permiso_name)
                
                if not tiene_permiso:
                    return jsonify({
                        'error': 'No tienes permisos para realizar esta acción',
                        'permiso_requerido': permiso_name
                    }), 403
                
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'Error al validar permisos',
                    'detail': str(e)
                }), 500
        return wrapper
    return decorator


def require_any_permission(*permissions):
    """
    Decorador para validar que el usuario tenga AL MENOS UNO de los permisos
    
    Args:
        *permissions: Lista de permisos, con uno es suficiente
    
    Usage:
        @router.route('/productos', methods=['PUT'])
        @jwt_required_custom()
        @require_any_permission('editar_productos', 'gestionar_productos')
        def editar_producto():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                usuario_id = get_jwt_identity()
                
                # Validar que tenga al menos uno de los permisos
                tiene_alguno = AuthService.validate_any_permission(usuario_id, list(permissions))
                
                if not tiene_alguno:
                    return jsonify({
                        'error': 'No tienes ninguno de los permisos requeridos',
                        'permisos_requeridos': list(permissions)
                    }), 403
                
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'Error al validar permisos',
                    'detail': str(e)
                }), 500
        return wrapper
    return decorator


def require_role(role_name: str):
    """
    Decorador para validar que el usuario tenga un rol específico
    
    Args:
        role_name: Nombre del rol (admin, maestro, supervisor, usuario)
    
    Usage:
        @router.route('/usuarios', methods=['POST'])
        @jwt_required_custom()
        @require_role('admin')
        def crear_usuario():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # Obtener claims del JWT
                claims = get_jwt()
                user_role = claims.get('rol')
                
                if user_role != role_name:
                    return jsonify({
                        'error': 'No tienes el rol requerido',
                        'rol_requerido': role_name,
                        'tu_rol': user_role
                    }), 403
                
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'Error al validar rol',
                    'detail': str(e)
                }), 500
        return wrapper
    return decorator


def require_any_role(*roles):
    """
    Decorador para validar que el usuario tenga AL MENOS UNO de los roles
    
    Args:
        *roles: Lista de roles
    
    Usage:
        @router.route('/productos', methods=['DELETE'])
        @jwt_required_custom()
        @require_any_role('admin', 'maestro')
        def eliminar_producto():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                claims = get_jwt()
                user_role = claims.get('rol')
                
                if user_role not in roles:
                    return jsonify({
                        'error': 'No tienes ninguno de los roles requeridos',
                        'roles_requeridos': list(roles),
                        'tu_rol': user_role
                    }), 403
                
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'Error al validar roles',
                    'detail': str(e)
                }), 500
        return wrapper
    return decorator


def get_current_user_id() -> int:
    """
    Helper para obtener el ID del usuario actual desde el JWT
    
    Returns:
        int: ID del usuario autenticado
    """
    return get_jwt_identity()


def get_current_user_role() -> str:
    """
    Helper para obtener el rol del usuario actual desde el JWT
    
    Returns:
        str: Rol del usuario (admin, maestro, supervisor, usuario)
    """
    claims = get_jwt()
    return claims.get('rol')


def get_client_ip() -> str:
    """
    Obtener la IP del cliente
    
    Returns:
        str: Dirección IP del cliente
    """
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr or 'unknown'


def get_user_agent() -> str:
    """
    Obtener el User Agent del cliente
    
    Returns:
        str: User Agent
    """
    return request.headers.get('User-Agent', 'unknown')