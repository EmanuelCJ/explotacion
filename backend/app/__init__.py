# Inicialización de Flask app
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import config
import os

jwt = JWTManager()

def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))
    
    # Inicializar extensiones
    jwt.init_app(app)
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'X-CSRF-TOKEN'])
    
    # Registrar Blueprints
    from app.routers.auth_routers import auth_bp
    from app.routers.usuario_routers import usuario_bp
    from app.routers.producto_routers import producto_bp
    from app.routers.categoria_routers import categoria_bp
    from app.routers.lugar_routers import lugar_bp
    from app.routers.movimiento_routers import movimiento_bp
    
    app.register_blueprint(auth_bp, url_prefix='/inventario/auth')
    app.register_blueprint(usuario_bp, url_prefix='/inventario/usuarios')
    app.register_blueprint(producto_bp, url_prefix='/inventario/productos')
    app.register_blueprint(categoria_bp, url_prefix='/inventario/categorias')
    app.register_blueprint(lugar_bp, url_prefix='/inventario/lugares')
    app.register_blueprint(movimiento_bp, url_prefix='/inventario/movimientos')
    
    # Manejadores de errores
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Recurso no encontrado'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Error interno del servidor'}, 500
    
    # JWT Error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return {'error': 'No autenticado. Token no proporcionado.'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return {'error': 'Token inválido'}, 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token expirado'}, 401
    
    return app