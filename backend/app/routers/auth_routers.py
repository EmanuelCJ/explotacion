from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies
)
from app.services.auth_service import AuthService
from app.services.auditoria_service import AuditoriaService

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()
auditoria_service = AuditoriaService()

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login de usuario
    Body: {
        "username": "usuario",
        "password": "contraseña"
    }
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'username y contraseña son requeridos'}), 400
        
        # Autenticar usuario
        usuario = auth_service.authenticate(username, password)
        
        if not usuario:
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        # Verificar si está activo
        if not usuario.get('activo'):
            return jsonify({'error': 'Usuario inactivo'}), 403
        
        # Crear tokens
        access_token = create_access_token(
            identity=usuario['id'],
            additional_claims={
                'username': usuario['username'],
                'rol': usuario['rol']
            }
        )
        refresh_token = create_refresh_token(identity=usuario['id'])
        
        # Registrar auditoría
        auditoria_service.registrar(
            usuario_id=usuario['id'],
            accion='LOGIN',
            tabla='usuarios',
            descripcion=f"Usuario {usuario['username']} inició sesión"
        )
        
        # Crear respuesta con cookies
        response = make_response(jsonify({
            'message': 'Login exitoso',
            'usuario': {
                'id': usuario['id'],
                'nombre': usuario['nombre'],
                'username': usuario['username'],
                'rol': usuario['rol']
            }
        }), 200)
        
        # Configurar cookies HttpOnly
        response.set_cookie(
            'access_token_cookie',
            value=access_token,
            httponly=True,
            secure=False,  # True en producción con HTTPS
            samesite='Lax',
            max_age=3600  # 1 hora
        )
        
        response.set_cookie(
            'refresh_token_cookie',
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=2592000  # 30 días
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Renovar access token usando refresh token"""
    try:
        current_user = get_jwt_identity()
        
        # Obtener datos actualizados del usuario
        usuario = auth_service.get_user_by_id(current_user)
        
        if not usuario or not usuario.get('activo'):
            return jsonify({'error': 'Usuario no encontrado o inactivo'}), 403
        
        # Crear nuevo access token
        access_token = create_access_token(
            identity=usuario['id'],
            additional_claims={
                'username': usuario['username'],
                'rol': usuario['rol']
            }
        )
        
        response = make_response(jsonify({'message': 'Token renovado'}), 200)
        
        response.set_cookie(
            'access_token_cookie',
            value=access_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=3600
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Cerrar sesión del usuario"""
    try:
        current_user = get_jwt_identity()
        
        # Registrar auditoría
        auditoria_service.registrar(
            usuario_id=current_user,
            accion='LOGOUT',
            tabla='usuarios',
            descripcion=f"Usuario {current_user} cerró sesión"
        )
        
        response = make_response(jsonify({'message': 'Logout exitoso'}), 200)
        unset_jwt_cookies(response)
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obtener información del usuario autenticado"""
    try:
        current_user = get_jwt_identity()
        usuario = auth_service.get_user_by_id(current_user)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'usuario': {
                'id': usuario['id'],
                'nombre': usuario['nombre'],
                'username': usuario['username'],
                'rol': usuario['rol'],
                'activo': usuario['activo']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verificar si el token es válido"""
    try:
        current_user = get_jwt_identity()
        return jsonify({
            'valid': True,
            'user_id': current_user
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500