import os
from app import create_app

# Crear aplicación
app = create_app()

if __name__ == '__main__':
    # Configuración de desarrollo
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5000))
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║  🚀 API REST - Sistema de Inventario    ║
    ╠══════════════════════════════════════════╣
    ║  Servidor: http://localhost:{port}       ║
    ║  Entorno: {os.getenv('FLASK_ENV', 'development')}                   ║
    ║  Debug: {debug_mode}                            ║
    ╚══════════════════════════════════════════╝
    
    Endpoints disponibles:
    
    🔐 Autenticación:
    POST   /api/auth/login       - Iniciar sesión
    POST   /api/auth/logout      - Cerrar sesión
    POST   /api/auth/refresh     - Renovar token
    GET    /api/auth/me          - Usuario actual
    GET    /api/auth/verify      - Verificar token
    
    📦 Productos:
    GET    /api/productos        - Listar productos
    GET    /api/productos/:id    - Obtener producto
    POST   /api/productos        - Crear producto
    PUT    /api/productos/:id    - Actualizar producto
    DELETE /api/productos/:id    - Eliminar producto
    GET    /api/productos/:id/stock        - Stock por lugar
    POST   /api/productos/:id/movimiento   - Crear movimiento
    GET    /api/productos/:id/historial    - Historial de movimientos
    
    👥 Usuarios:
    GET    /api/usuarios         - Listar usuarios
    GET    /api/usuarios/:id     - Obtener usuario
    POST   /api/usuarios         - Crear usuario
    PUT    /api/usuarios/:id     - Actualizar usuario
    DELETE /api/usuarios/:id     - Eliminar usuario
    
    📁 Categorías:
    GET    /api/categorias       - Listar categorías
    POST   /api/categorias       - Crear categoría
    PUT    /api/categorias/:id   - Actualizar categoría
    DELETE /api/categorias/:id   - Eliminar categoría
    
    📍 Lugares:
    GET    /api/lugares          - Listar lugares
    POST   /api/lugares          - Crear lugar
    PUT    /api/lugares/:id      - Actualizar lugar
    DELETE /api/lugares/:id      - Eliminar lugar
    
    📊 Movimientos:
    GET    /api/movimientos      - Listar movimientos
    GET    /api/movimientos/:id  - Obtener movimiento
    """)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )