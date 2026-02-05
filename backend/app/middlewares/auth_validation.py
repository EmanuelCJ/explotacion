# app/middlewares/auth_validation.py

"""
Decorador de validación para endpoints de autenticación
Protege contra SQL injection y valida formato de credenciales
"""

from functools import wraps
from flask import request, jsonify
import re


def validate_credentials(require_current_password=False):
    """
    Valida credenciales de login/cambio de contraseña
    
    Validaciones:
    - Username/password deben ser strings
    - Password mínimo 6 caracteres
    - Username sin caracteres especiales peligrosos
    - Sanitización contra SQL injection
    
    Args:
        require_current_password (bool): True para cambio de contraseña
    
    Usage:
        @auth_bp.route('/login', methods=['POST'])
        @validate_credentials()
        def login():
            ...
        
        @auth_bp.route('/change-password', methods=['POST'])
        @validate_credentials(require_current_password=True)
        def change_password():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json()
                
                # Validar que venga JSON
                if not data:
                    return jsonify({
                        'error': 'Datos faltantes',
                        'detail': 'El body debe contener JSON válido'
                    }), 400
                
                # Para login
                if not require_current_password:
                    username = data.get('username')
                    password = data.get('password')
                    
                    # Validar campos requeridos
                    if not username or not password:
                        return jsonify({
                            'error': 'Datos incompletos',
                            'detail': 'Username y password son requeridos'
                        }), 400
                    
                    # Validar tipos
                    if not isinstance(username, str) or not isinstance(password, str):
                        return jsonify({
                            'error': 'Tipo de dato inválido',
                            'detail': 'Username y password deben ser strings'
                        }), 400
                    
                    # Validar longitud mínima de password
                    if len(password) < 6:
                        return jsonify({
                            'error': 'Password inválido',
                            'detail': 'El password debe tener al menos 6 caracteres'
                        }), 400
                    
                    # Validar longitud de username
                    if len(username) < 3 or len(username) > 50:
                        return jsonify({
                            'error': 'Username inválido',
                            'detail': 'El username debe tener entre 3 y 50 caracteres'
                        }), 400
                    
                    # Sanitizar username - solo alfanuméricos, guiones y guión bajo
                    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
                        return jsonify({
                            'error': 'Username inválido',
                            'detail': 'El username solo puede contener letras, números, guiones y guión bajo'
                        }), 400
                    
                    # Protección contra patrones de SQL injection
                    sql_patterns = [
                        r"('|(\\')|(;)|(--)|(\/\*)|(xp_))",  # Comillas, comentarios SQL
                        r"(\bunion\b.*\bselect\b)",  # UNION SELECT
                        r"(\bdrop\b.*\btable\b)",  # DROP TABLE
                        r"(\binsert\b.*\binto\b)",  # INSERT INTO
                        r"(\bupdate\b.*\bset\b)",  # UPDATE SET
                        r"(\bdelete\b.*\bfrom\b)",  # DELETE FROM
                    ]
                    
                    username_lower = username.lower()
                    password_lower = password.lower()
                    
                    for pattern in sql_patterns:
                        if re.search(pattern, username_lower, re.IGNORECASE):
                            return jsonify({
                                'error': 'Datos sospechosos detectados',
                                'detail': 'El username contiene caracteres no permitidos'
                            }), 400
                        if re.search(pattern, password_lower, re.IGNORECASE):
                            return jsonify({
                                'error': 'Datos sospechosos detectados',
                                'detail': 'El password contiene patrones no permitidos'
                            }), 400
                #agregar validacion de para cuando mandan un id ejemplo sea positivo y no contenga letras, no sql injection

                
                
                # Para cambio de contraseña
                else:
                    password_actual = data.get('password_actual')
                    password_nuevo = data.get('password_nuevo')
                    
                    # Validar campos requeridos
                    if not password_actual or not password_nuevo:
                        return jsonify({
                            'error': 'Datos incompletos',
                            'detail': 'Password actual y nuevo son requeridos'
                        }), 400
                    
                    # Validar tipos
                    if not isinstance(password_actual, str) or not isinstance(password_nuevo, str):
                        return jsonify({
                            'error': 'Tipo de dato inválido',
                            'detail': 'Los passwords deben ser strings'
                        }), 400
                    
                    # Validar longitud mínima
                    if len(password_nuevo) < 6:
                        return jsonify({
                            'error': 'Password nuevo inválido',
                            'detail': 'El password debe tener al menos 6 caracteres'
                        }), 400
                    
                    # Validar longitud máxima (prevenir DoS)
                    if len(password_nuevo) > 128 or len(password_actual) > 128:
                        return jsonify({
                            'error': 'Password demasiado largo',
                            'detail': 'El password no puede exceder 128 caracteres'
                        }), 400
                    
                    # Validar que sean diferentes
                    if password_actual == password_nuevo:
                        return jsonify({
                            'error': 'Password inválido',
                            'detail': 'El password nuevo debe ser diferente al actual'
                        }), 400
                    
                    # Protección contra SQL injection en passwords
                    sql_patterns = [
                        r"('|(\\')|(;)|(--)|(\/\*))",
                        r"(\bunion\b.*\bselect\b)",
                        r"(\bdrop\b.*\btable\b)",
                    ]
                    
                    for pattern in sql_patterns:
                        if re.search(pattern, password_nuevo.lower(), re.IGNORECASE):
                            return jsonify({
                                'error': 'Password inválido',
                                'detail': 'El password contiene patrones no permitidos'
                            }), 400
                
                # Si pasa todas las validaciones, ejecutar la función
                return fn(*args, **kwargs)
                
            except Exception as e:
                return jsonify({
                    'error': 'Error al validar datos',
                    'detail': str(e)
                }), 500
        
        return wrapper
    return decorator


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitiza un string para prevenir SQL injection
    
    Args:
        value: String a sanitizar
        max_length: Longitud máxima permitida
    
    Returns:
        String sanitizado
    """
    if not isinstance(value, str):
        raise ValueError("El valor debe ser un string")
    
    # Truncar si es muy largo
    value = value[:max_length]
    
    # Eliminar caracteres peligrosos
    dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_']
    for char in dangerous_chars:
        value = value.replace(char, '')
    
    return value.strip()