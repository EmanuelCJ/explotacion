"""
Archivo principal para ejecutar el servidor
Aguas Rionegrinas - Sistema de Inventario
"""

import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False") == "True"


    print("\n" + "="*70)
    print("🌊 AGUAS RIONEGRINAS - SISTEMA DE INVENTARIO")
    print("="*70)
    print(f"\n📍 Servidor: http://{host}:{port}")
    print(f"🔧 Entorno: {os.getenv('FLASK_ENV', 'development')}")
    print(f"🐛 Debug: {debug}")
    print("\n📋 ENDPOINTS DISPONIBLES:\n")
    print("🔐 Autenticación:")
    print("   POST   /api/auth/login")
    print("   POST   /api/auth/logout")
    print("   POST   /api/auth/refresh")
    print("   GET    /api/auth/me")
    print("\n📦 Productos:")
    print("   GET    /api/productos")
    print("   POST   /api/productos")
    print("   PUT    /api/productos/:id")
    print("   DELETE /api/productos/:id")
    print("\n🔄 Movimientos:")
    print("   POST   /api/movimientos/entrada")
    print("   POST   /api/movimientos/salida")
    print("   POST   /api/movimientos/transferencia")
    print("\n📤 Envíos:")
    print("   POST   /api/envios")
    print("   POST   /api/envios/:id/recibir")
    print("   POST   /api/envios/:id/cancelar")
    print("\n" + "="*70 + "\n")
    
    # Ejecutar servidor
    app.run(
        host=host,
        port=port,
        debug=debug
    )