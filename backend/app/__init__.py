"""
Aplicación Flask - Aguas Rionegrinas
Inicialización y registro de routers
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

jwt = JWTManager()

def create_app():
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # ========================================
    # CONFIGURACIÓN
    # ========================================
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # JWT en cookies HttpOnly
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_HTTPONLY'] = True
    app.config['JWT_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Desactivar CSRF en desarrollo
    
    # CORS
    app.config['CORS_ORIGINS'] = os.getenv('CORS_ORIGINS', 'http://localhost:8080').split(',')
    
    # ========================================
    # EXTENSIONES
    # ========================================
    jwt.init_app(app)
    
    CORS(app,
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'])
    
    # ========================================
    # REGISTRAR BLUEPRINTS/ROUTERS
    # ========================================
    from app.routers.auth_routers import auth_bp
    from app.routers.producto_routers import producto_bp
    from app.routers.movimiento_routers import movimiento_bp
    from app.routers.envio_routers import envio_bp
    # Importar los demás cuando los crees:
    # from app.routers.usuario_routers import usuario_bp
    # from app.routers.auditoria_routers import auditoria_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(producto_bp, url_prefix='/api/productos')
    app.register_blueprint(movimiento_bp, url_prefix='/api/movimientos')
    app.register_blueprint(envio_bp, url_prefix='/api/envios')
    # app.register_blueprint(usuario_bp, url_prefix='/api/usuarios')
    # app.register_blueprint(auditoria_bp, url_prefix='/api/auditoria')
    
    # ========================================
    # MANEJADORES DE ERRORES
    # ========================================
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint no encontrado'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Error interno del servidor'}, 500
    
    # JWT Error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return {'error': 'Token no proporcionado'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return {'error': 'Token inválido'}, 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token expirado'}, 401
    
    @app.route('/')
    def index():
        return {
            'app': 'Aguas Rionegrinas - Sistema de Inventario',
            'version': '1.0.0',
            'status': 'running'
        }
    
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200
    
    return app