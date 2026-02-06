"""
Aplicación Flask - Aguas Rionegrinas
Inicialización y registro de routers
"""

from flask import Flask
from dotenv import load_dotenv

from .config import Config
from .extensions import jwt, cors

# Blueprints
from .routers.auth_routers import auth_bp
from .routers.usuario_routers import usuario_bp
from .routers.producto_routers import producto_bp
from .routers.movimiento_routers import movimiento_bp
from .routers.envio_routers import envio_bp
from .routers.auditoria_routers import auditoria_bp

def create_app():
    
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensiones
    jwt.init_app(app)

    cors.init_app(
        app,
        supports_credentials=True,
        origins=app.config["CORS_ORIGINS"]
    )

    # Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(usuario_bp, url_prefix="/api/usuarios")
    app.register_blueprint(producto_bp, url_prefix="/api/productos")
    app.register_blueprint(movimiento_bp, url_prefix="/api/movimientos")
    app.register_blueprint(envio_bp, url_prefix="/api/envios")
    app.register_blueprint(auditoria_bp, url_prefix="/api/auditoria")

    
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