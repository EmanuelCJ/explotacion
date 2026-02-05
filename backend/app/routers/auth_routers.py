"""
Router de Autenticación
Endpoints: login, logout, refresh, me, verify
Maneja JWT en cookies HttpOnly
"""

from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies
)
from app.services.auth_service import AuthService
from app.middlewares.auth_validation import validate_credentials
from app.utils.decoradores_auth import get_client_ip, get_user_agent, jwt_required_cookie
from datetime import timedelta


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
@validate_credentials()
def login():
    """
    Login de usuario
    
    Body:
    {
        "username": "admin",
        "password": "comahue719"
    }
    
    Returns:
        200: Login exitoso con datos del usuario
        400: Datos faltantes
        401: Credenciales inválidas
    """
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username y password son requeridos'}), 400
        
        username = data.get('username')
        password = data.get('password')

        # Obtener IP del cliente para auditoría
        ip_address = get_client_ip()

        # Autenticar
        usuario = AuthService.authenticate(username, password, ip_address)

        
        if not usuario:
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        # Crear tokens JWT
        # Access token con información del usuario
        access_token = create_access_token(
            identity=usuario['id_usuario'],
            additional_claims={
                'username': usuario['username'],
                'rol': usuario['roles'].split(',')[0] if usuario.get('roles') else 'usuario',
                'localidad_id': usuario['id_localidad']
            },
            expires_delta=timedelta(hours=1)  # 1 hora
        )
        
        # Refresh token
        refresh_token = create_refresh_token(
            identity=usuario['id_usuario'],
            expires_delta=timedelta(days=30)  # 30 días
        )
        
        # Crear respuesta
        response = make_response(jsonify({
            'message': 'Login exitoso',
            'usuario': {
                'id': usuario['id_usuario'],
                'nombre': usuario['nombre'],
                'apellido': usuario['apellido'],
                'username': usuario['username'],
                'email': usuario.get('email'),
                'rol': usuario['roles'].split(',')[0] if usuario.get('roles') else 'usuario',
                'localidad': usuario.get('localidad_nombre'),
                'permisos': usuario.get('permisos', [])
            }
        }), 200)
        
        # Configurar cookies HttpOnly
        # IMPORTANTE: httponly=True para que JavaScript no pueda acceder
        response.set_cookie(
            'access_token_cookie',
            value=access_token,
            httponly=True,
            secure=False,  # True en producción con HTTPS
            samesite='Lax',
            max_age=3600  # 1 hora en segundos
        )
        
        response.set_cookie(
            'refresh_token_cookie',
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=2592000  # 30 días en segundos
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required_cookie()
def logout():
    """
    Cerrar sesión del usuario
    Elimina las cookies JWT
    
    Returns:
        200: Logout exitoso
    """
    try:
        usuario_id = get_jwt_identity()
        ip_address = get_client_ip()
        
        # Registrar logout
        AuthService.logout(usuario_id, ip_address)
        
        # Crear respuesta
        response = make_response(jsonify({'message': 'Logout exitoso'}), 200)
        
        # Eliminar cookies JWT
        unset_jwt_cookies(response)
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Renovar access token usando refresh token
    El refresh token debe estar en la cookie
    
    Returns:
        200: Nuevo access token
        401: Refresh token inválido
    """
    try:
        usuario_id = get_jwt_identity()
        
        # Obtener datos actualizados del usuario
        usuario = AuthService.get_user_by_id(usuario_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        if not usuario.get('activo'):
            return jsonify({'error': 'Usuario inactivo'}), 403
        
        # Crear nuevo access token
        access_token = create_access_token(
            identity=usuario_id,
            additional_claims={
                'username': usuario['username'],
                'rol': usuario['roles'].split(',')[0] if usuario.get('roles') else 'usuario',
                'localidad_id': usuario['id_localidad']
            },
            expires_delta=timedelta(hours=1)
        )
        
        # Crear respuesta
        response = make_response(jsonify({'message': 'Token renovado'}), 200)
        
        # Actualizar cookie de access token
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


@auth_bp.route('/me', methods=['GET'])
@jwt_required_cookie()
def get_current_user():
    """
    Obtener información del usuario autenticado
    
    Returns:
        200: Datos del usuario actual
        404: Usuario no encontrado
    """
    try:
        usuario_id = get_jwt_identity()
        
        # Obtener datos del usuario
        usuario = AuthService.get_user_by_id(usuario_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'usuario': {
                'id': usuario['id_usuario'],
                'nombre': usuario['nombre'],
                'apellido': usuario['apellido'],
                'username': usuario['username'],
                'email': usuario.get('email'),
                'legajo': usuario.get('legajo'),
                'rol': usuario['roles'].split(',')[0] if usuario.get('roles') else 'usuario',
                'localidad': usuario.get('localidad_nombre'),
                'activo': usuario['activo']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/verify', methods=['GET'])
@jwt_required_cookie()
def verify_token():
    """
    Verificar si el token es válido
    Útil para el frontend para verificar sesión
    
    Returns:
        200: Token válido
        401: Token inválido
    """
    try:
        usuario_id = get_jwt_identity()
        
        return jsonify({
            'valid': True,
            'usuario_id': usuario_id
        }), 200
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 401


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required_cookie()
@validate_credentials(require_current_password=True)
def change_password():
    """
    Cambiar contraseña del usuario actual
    
    Body:
    {
        "password_actual": "oldpassword",
        "password_nuevo": "newpassword"
    }
    
    Returns:
        200: Contraseña cambiada
        400: Datos inválidos
    """
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar datos
        if not data or not data.get('password_actual') or not data.get('password_nuevo'):
            return jsonify({'error': 'Password actual y nuevo son requeridos'}), 400
        
        # Cambiar password
        success = AuthService.change_password(
            usuario_id,
            data['password_actual'],
            data['password_nuevo']
        )
        
        if success:
            return jsonify({'message': 'Contraseña actualizada correctamente'}), 200
        else:
            return jsonify({'error': 'No se pudo actualizar la contraseña'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400