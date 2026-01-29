from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt

def require_role(allowed_roles):
    """
    Decorador para validar roles de usuario
    
    Uso:
    @require_role(['admin', 'gestor'])
    def mi_funcion():
        pass
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('rol')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'No tienes permisos para realizar esta acción',
                    'required_roles': allowed_roles,
                    'your_role': user_role
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def is_admin():
    """Verificar si el usuario actual es admin"""
    claims = get_jwt()
    return claims.get('rol') == 'admin'

def is_gestor():
    """Verificar si el usuario actual es gestor"""
    claims = get_jwt()
    return claims.get('rol') in ['admin', 'gestor']

def is_operador():
    """Verificar si el usuario actual es operador"""
    claims = get_jwt()
    return claims.get('rol') in ['admin', 'gestor', 'operador']