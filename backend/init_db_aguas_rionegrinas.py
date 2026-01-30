"""
Script de inicialización de base de datos
Sistema de Inventario - Aguas Rionegrinas
Río Negro, Argentina
"""

import pymysql
import bcrypt
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'charset': 'utf8mb4'
}

DB_NAME = os.getenv('DB_NAME', 'aguas_rionegrinas_db')


def create_database():
    """Crear base de datos si no existe"""
    print("\n" + "="*70)
    print("🌊 AGUAS RIONEGRINAS - SISTEMA DE INVENTARIO")
    print("="*70)
    print("\n📦 Creando base de datos...")
    
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS {DB_NAME} 
                CHARACTER SET utf8mb4 
                COLLATE utf8mb4_unicode_ci
            """)
            print(f"✅ Base de datos '{DB_NAME}' creada/verificada")
    finally:
        connection.close()


def create_tables():
    """Crear todas las tablas del sistema"""
    print("\n📊 Creando tablas...")
    
    config = DB_CONFIG.copy()
    config['database'] = DB_NAME
    connection = pymysql.connect(**config)
    
    try:
        with connection.cursor() as cursor:
            
            # ========================================
            # TABLA: LOCALIDADES (Sedes de Aguas Rionegrinas)
            # ========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS localidades (
                    id_localidad INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL UNIQUE,
                    descripcion TEXT,
                    direccion VARCHAR(255),
                    ciudad VARCHAR(100),
                    codigo_postal VARCHAR(20),
                    activo TINYINT(1) DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_nombre (nombre),
                    INDEX idx_activo (activo),
                    INDEX idx_ciudad (ciudad)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("  ✓ Tabla 'localidades' creada")
            
            # ========================================
            # TABLA: ROLES (4 roles jerárquicos)
            # ========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    id_rol INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(50) NOT NULL UNIQUE,
                    descripcion VARCHAR(255) NOT NULL,
                    nivel INT NOT NULL COMMENT '1=Admin, 2=Maestro, 3=Supervisor, 4=Usuario',
                    activo TINYINT(1) DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_nombre (nombre),
                    INDEX idx_nivel (nivel),
                    INDEX idx_activo (activo)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("  ✓ Tabla 'roles' creada")
            
            # ========================================
            # TABLA: PERMISOS
            # ========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS permisos (
                    id_permiso INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(50) NOT NULL UNIQUE,
                    descripcion VARCHAR(255) NOT NULL,
                    recurso VARCHAR(50) NOT NULL COMMENT 'usuarios, productos, movimientos, envios, etc.',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_nombre (nombre),
                    INDEX idx_recurso (recurso)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("  ✓ Tabla 'permisos' creada")
            
            # ========================================
            # TABLA: ROLES_PERMISOS
            # ========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roles_permisos (
                    id_rol INT NOT NULL,
                    id_permiso INT NOT NULL,
                    PRIMARY KEY (id_rol, id_permiso),
                    FOREIGN KEY (id_rol) REFERENCES roles(id_rol) ON DELETE CASCADE,
                    FOREIGN KEY (id_permiso) REFERENCES permisos(id_permiso) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("  ✓ Tabla 'roles_permisos' creada")
            
            # ========================================
            # TABLA: USUARIOS
            # ========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(50) NOT NULL,
                    apellido VARCHAR(50) NOT NULL,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    legajo VARCHAR(50) NULL COMMENT 'Número de legajo del empleado',
                    id_localidad INT NOT NULL COMMENT 'Localidad a la que pertenece',
                    activo TINYINT(1) DEFAULT 1,
                    ultimo_login TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_localidad) REFERENCES localidades(id_localidad),
                    INDEX idx_username (username),
                    INDEX idx_email (email),
                    INDEX idx_activo (activo),
                    INDEX idx_localidad (id_localidad),
                    INDEX idx_legajo (legajo)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("  ✓ Tabla 'usuarios' creada")
            
            # ========================================
            # TABLA: USUARIOS_ROLES
            # ========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios_roles (
                    id_usuario INT NOT NULL,
                    id_rol INT NOT NULL,
                    asignado_por INT COMMENT 'Usuario que asignó el rol',
                    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (id_usuario, id_rol),
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
                    FOREIGN KEY (id_rol) REFERENCES roles(id_rol) ON DELETE CASCADE,
                    FOREIGN KEY (asignado_por) REFERENCES usuarios(id_usuario)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("  ✓ Tabla 'usuarios_roles' creada")
            
            # ========================================
            # TABLA: CATEGORIAS
            # ========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categorias (
                    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
                    tipo VARCHAR(50) NOT NULL COMMENT 'Tipo de categoría',
                    nombre VARCHAR(100) NOT NULL,
                    codigo VARCHAR(50) UNIQUE COMMENT 'Código único de categoría',
                    descripcion TEXT,
                    activo TINYINT(1) DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_nombre (nombre),
                    INDEX idx_tipo (tipo),
                    INDEX idx_codigo (codigo),
                    INDEX idx_activo (activo)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("  ✓ Tabla 'categorias' creada")
            
            # ========================================
            # TABLA: LUGARES (Dentro de cada localidad)
            # ========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lugares (
                    id_lugar INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT COMMENT 'Servicio, planta, almacén, etc.',
                    tipo ENUM('servicio', 'planta', 'almacen', 'deposito', 'otro') DEFAULT 'almacen',
                    id_localidad INT NOT NULL COMMENT 'Localidad a la que pertenece',
                    activo TINYINT(1) DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_localidad) REFERENCES localidades(id_localidad),
                    INDEX idx_nombre (nombre),
                    INDEX idx_tipo (tipo),
                    INDEX idx_localidad (id_localidad),
                    INDEX idx_activo (activo)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("  ✓ Tabla 'lugares' creada")
            
            # ========================================
            # TABLA: PRODUCTOS
            # ========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id_producto INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(200) NOT NULL,
                    codigo VARCHAR(50) UNIQUE COMMENT 'Código del producto',
                    descripcion TEXT,
                    id_categoria INT NOT NULL,
                    costo DECIMAL(10, 2) NULL COMMENT 'Costo unitario (opcional)',
                    unidad_medida VARCHAR(20) COMMENT 'kg, lt, unidad, etc.',
                    stock_minimo INT DEFAULT 0,
                    activo TINYINT(1) DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
                    INDEX idx_nombre (nombre),
                    INDEX idx_codigo (codigo),
                    INDEX idx_categoria (id_categoria),
                    INDEX idx_activo (activo)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("  ✓ Tabla 'productos' creada")
            
            # ========================================
            # TABLA: PRODUCTOS_LOCALIDAD (Stock por localidad y lugar)
            # ========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos_localidad (
                    id_producto INT NOT NULL,
                    id_localidad INT NOT NULL,
                    id_lugar INT NOT NULL COMMENT 'Lugar específico dentro de la localidad',
                    cantidad INT NOT NULL DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (id_producto, id_localidad, id_lugar),
                    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
                    FOREIGN KEY (id_localidad) REFERENCES localidades(id_localidad) ON DELETE CASCADE,
                    FOREIGN KEY (id_lugar) REFERENCES lugares(id_lugar) ON DELETE CASCADE,
                    INDEX idx_producto (id_producto),
                    INDEX idx_localidad (id_localidad),
                    INDEX idx_lugar (id_lugar)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("  ✓ Tabla 'productos_localidad' creada")
            
            # ========================================
            # TABLA: MOVIMIENTOS
            # ========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movimientos (
                    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
                    tipo ENUM('entrada', 'salida', 'transferencia', 'ajuste') NOT NULL,
                    cantidad INT NOT NULL,
                    id_producto INT NOT NULL,
                    id_usuario INT NOT NULL COMMENT 'Usuario que realizó el movimiento',
                    id_localidad INT NOT NULL COMMENT 'Localidad donde se realizó',
                    lugar_origen INT NULL COMMENT 'Lugar de origen (para transferencias)',
                    lugar_destino INT NULL COMMENT 'Lugar de destino',
                    motivo VARCHAR(255) COMMENT 'Razón del movimiento',
                    observaciones TEXT,
                    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                    FOREIGN KEY (id_localidad) REFERENCES localidades(id_localidad),
                    FOREIGN KEY (lugar_origen) REFERENCES lugares(id_lugar),
                    FOREIGN KEY (lugar_destino) REFERENCES lugares(id_lugar),
                    INDEX idx_producto (id_producto),
                    INDEX idx_usuario (id_usuario),
                    INDEX idx_localidad (id_localidad),
                    INDEX idx_tipo (tipo),
                    INDEX idx_fecha (fecha_hora)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("  ✓ Tabla 'movimientos' creada")
            
            # ========================================
            # TABLA: ENVIOS (Entre localidades)
            # ========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS envios (
                    id_envio INT AUTO_INCREMENT PRIMARY KEY,
                    id_producto INT NOT NULL,
                    cantidad INT NOT NULL,
                    id_usuario_envia INT NOT NULL COMMENT 'Usuario que envía',
                    id_usuario_recibe INT NULL COMMENT 'Usuario que recibe',
                    localidad_origen INT NOT NULL,
                    localidad_destino INT NOT NULL,
                    lugar_origen INT NOT NULL,
                    lugar_destino INT NULL,
                    estado ENUM('enviado', 'en_transito', 'recibido', 'cancelado') DEFAULT 'enviado',
                    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_recepcion TIMESTAMP NULL,
                    fecha_cancelacion TIMESTAMP NULL,
                    motivo VARCHAR(255) COMMENT 'Motivo del envío',
                    observaciones_envio TEXT,
                    observaciones_recepcion TEXT,
                    observaciones_cancelacion TEXT,
                    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
                    FOREIGN KEY (id_usuario_envia) REFERENCES usuarios(id_usuario),
                    FOREIGN KEY (id_usuario_recibe) REFERENCES usuarios(id_usuario),
                    FOREIGN KEY (localidad_origen) REFERENCES localidades(id_localidad),
                    FOREIGN KEY (localidad_destino) REFERENCES localidades(id_localidad),
                    FOREIGN KEY (lugar_origen) REFERENCES lugares(id_lugar),
                    FOREIGN KEY (lugar_destino) REFERENCES lugares(id_lugar),
                    INDEX idx_producto (id_producto),
                    INDEX idx_usuario_envia (id_usuario_envia),
                    INDEX idx_usuario_recibe (id_usuario_recibe),
                    INDEX idx_localidad_origen (localidad_origen),
                    INDEX idx_localidad_destino (localidad_destino),
                    INDEX idx_estado (estado),
                    INDEX idx_fecha_envio (fecha_envio)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("  ✓ Tabla 'envios' creada")
            
            # ========================================
            # TABLA: AUDITORIA
            # ========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auditoria (
                    id_auditoria INT AUTO_INCREMENT PRIMARY KEY,
                    entidad VARCHAR(50) NOT NULL COMMENT 'Usuario, Producto, Envio, etc.',
                    id_entidad INT NOT NULL COMMENT 'ID del registro afectado',
                    accion ENUM('create', 'update', 'delete', 'login', 'logout', 
                                'envio', 'recepcion', 'cancelacion', 'ajuste') NOT NULL,
                    descripcion TEXT COMMENT 'Descripción de la acción',
                    datos_anteriores JSON COMMENT 'Estado antes del cambio',
                    datos_nuevos JSON COMMENT 'Estado después del cambio',
                    id_usuario INT NOT NULL COMMENT 'Usuario que realizó la acción',
                    ip_address VARCHAR(45),
                    user_agent VARCHAR(255),
                    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                    INDEX idx_entidad (entidad),
                    INDEX idx_id_entidad (id_entidad),
                    INDEX idx_usuario (id_usuario),
                    INDEX idx_accion (accion),
                    INDEX idx_fecha (fecha_hora)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("  ✓ Tabla 'auditoria' creada")
            
        connection.commit()
        print("\n✅ Todas las tablas creadas correctamente")
        
    except Exception as e:
        connection.rollback()
        print(f"\n❌ Error al crear tablas: {e}")
        raise
    finally:
        connection.close()


def insert_initial_data():
    """Insertar datos iniciales del sistema"""
    print("\n📝 Insertando datos iniciales...")
    
    config = DB_CONFIG.copy()
    config['database'] = DB_NAME
    connection = pymysql.connect(**config)
    
    try:
        with connection.cursor() as cursor:
            
            # ========================================
            # LOCALIDADES DE RÍO NEGRO
            # ========================================
            print("\n  📍 Insertando localidades de Río Negro...")
            cursor.execute("""
                INSERT INTO localidades (nombre, descripcion, ciudad) VALUES
                ('Viedma', 'Sede Central - Capital de Río Negro', 'Viedma'),
                ('San Carlos de Bariloche', 'Sede Bariloche', 'San Carlos de Bariloche'),
                ('General Roca', 'Sede General Roca', 'General Roca'),
                ('Cipolletti', 'Sede Cipolletti', 'Cipolletti'),
                ('Choele Choel', 'Sede Choele Choel', 'Choele Choel'),
                ('El Bolsón', 'Sede El Bolsón', 'El Bolsón'),
                ('Villa Regina', 'Sede Villa Regina', 'Villa Regina'),
                ('Cinco Saltos', 'Sede Cinco Saltos', 'Cinco Saltos')
                ON DUPLICATE KEY UPDATE nombre=VALUES(nombre)
            """)
            print("    ✓ 8 localidades de Río Negro insertadas")
            
            # ========================================
            # ROLES (4 roles jerárquicos)
            # ========================================
            print("\n  👥 Insertando roles...")
            cursor.execute("""
                INSERT INTO roles (nombre, descripcion, nivel) VALUES
                ('admin', 'Administrador - Control total del sistema', 1),
                ('maestro', 'Maestro - Gestión completa y auditoría', 2),
                ('supervisor', 'Supervisor - Operaciones y reportes', 3),
                ('usuario', 'Usuario - Operaciones básicas', 4)
                ON DUPLICATE KEY UPDATE descripcion=VALUES(descripcion)
            """)
            print("    ✓ 4 roles creados")
            
            # ========================================
            # PERMISOS
            # ========================================
            print("\n  🔐 Insertando permisos...")
            cursor.execute("""
                INSERT INTO permisos (nombre, descripcion, recurso) VALUES
                -- USUARIOS (solo admin)
                ('crear_usuarios', 'Crear nuevos usuarios', 'usuarios'),
                ('editar_usuarios', 'Modificar usuarios existentes', 'usuarios'),
                ('eliminar_usuarios', 'Eliminar usuarios', 'usuarios'),
                ('asignar_roles', 'Asignar roles a usuarios', 'usuarios'),
                ('ver_usuarios', 'Ver lista de usuarios', 'usuarios'),
                
                -- PRODUCTOS (CRUD)
                ('crear_productos', 'Crear nuevos productos', 'productos'),
                ('editar_productos', 'Modificar productos', 'productos'),
                ('eliminar_productos', 'Eliminar productos', 'productos'),
                ('ver_productos', 'Visualizar productos', 'productos'),
                
                -- MOVIMIENTOS
                ('registrar_entrada', 'Registrar entradas de stock', 'movimientos'),
                ('registrar_salida', 'Registrar salidas de stock', 'movimientos'),
                ('registrar_transferencia', 'Transferir entre lugares', 'movimientos'),
                ('registrar_ajuste', 'Realizar ajustes de inventario', 'movimientos'),
                ('ver_movimientos', 'Ver historial de movimientos', 'movimientos'),
                
                -- ENVÍOS
                ('enviar_productos', 'Enviar productos a otras localidades', 'envios'),
                ('recibir_productos', 'Recibir productos enviados', 'envios'),
                ('cancelar_envios', 'Cancelar envíos', 'envios'),
                ('ver_envios', 'Ver lista de envíos', 'envios'),
                
                -- AUDITORÍA (maestro y supervisor)
                ('ver_auditoria', 'Ver registro de auditoría', 'auditoria'),
                ('ver_auditoria_usuario', 'Ver qué hizo cada usuario', 'auditoria'),
                ('exportar_auditoria', 'Exportar datos de auditoría', 'auditoria'),
                
                -- REPORTES
                ('crear_reportes', 'Crear reportes personalizados', 'reportes'),
                ('ver_reportes', 'Ver reportes del sistema', 'reportes'),
                ('exportar_reportes', 'Exportar reportes', 'reportes'),
                
                -- CATEGORÍAS Y LUGARES
                ('gestionar_categorias', 'Crear/editar categorías', 'categorias'),
                ('gestionar_lugares', 'Crear/editar lugares', 'lugares')
                ON DUPLICATE KEY UPDATE descripcion=VALUES(descripcion)
            """)
            print("    ✓ 27 permisos creados")
            
            # ========================================
            # ASIGNACIÓN DE PERMISOS A ROLES
            # ========================================
            print("\n  🔗 Asignando permisos a roles...")
            
            # ROL ADMIN (1) - TODOS los permisos
            cursor.execute("""
                INSERT IGNORE INTO roles_permisos (id_rol, id_permiso)
                SELECT 1, id_permiso FROM permisos
            """)
            print("    ✓ Admin: TODOS los permisos")
            
            # ROL MAESTRO (2) - Todo EXCEPTO gestión de usuarios
            cursor.execute("""
                INSERT IGNORE INTO roles_permisos (id_rol, id_permiso)
                SELECT 2, id_permiso FROM permisos 
                WHERE nombre NOT IN ('crear_usuarios', 'editar_usuarios', 
                                    'eliminar_usuarios', 'asignar_roles')
            """)
            print("    ✓ Maestro: CRUD, envíos, auditoría y reportes")
            
            # ROL SUPERVISOR (3) - CRUD, envíos y reportes (NO auditoría de usuario)
            cursor.execute("""
                INSERT IGNORE INTO roles_permisos (id_rol, id_permiso)
                SELECT 3, id_permiso FROM permisos 
                WHERE nombre IN (
                    'ver_usuarios',
                    'crear_productos', 'editar_productos', 'ver_productos',
                    'registrar_entrada', 'registrar_salida', 'registrar_transferencia',
                    'registrar_ajuste', 'ver_movimientos',
                    'enviar_productos', 'recibir_productos', 'cancelar_envios', 'ver_envios',
                    'crear_reportes', 'ver_reportes', 'exportar_reportes'
                )
            """)
            print("    ✓ Supervisor: CRUD, envíos y reportes")
            
            # ROL USUARIO (4) - Solo operaciones básicas
            cursor.execute("""
                INSERT IGNORE INTO roles_permisos (id_rol, id_permiso)
                SELECT 4, id_permiso FROM permisos 
                WHERE nombre IN (
                    'ver_productos', 'crear_productos', 'editar_productos',
                    'registrar_entrada', 'registrar_salida', 'registrar_transferencia',
                    'ver_movimientos',
                    'enviar_productos', 'recibir_productos', 'ver_envios'
                )
            """)
            print("    ✓ Usuario: Operaciones básicas")
            
            # ========================================
            # USUARIO ADMINISTRADOR
            # ========================================
            print("\n  👑 Creando usuario administrador...")
            
            # Hashear password: comahue719
            password = 'comahue719'
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Obtener ID de Viedma (primera localidad)
            cursor.execute("SELECT id_localidad FROM localidades WHERE nombre = 'Viedma' LIMIT 1")
            id_viedma = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO usuarios 
                (nombre, apellido, username, email, password_hash, id_localidad, activo)
                VALUES ('Administrador', 'Sistema', 'admin', 'admin@aguasrionegrinas.gov.ar', %s, %s, 1)
                ON DUPLICATE KEY UPDATE password_hash=VALUES(password_hash)
            """, (password_hash, id_viedma))
            
            # Asignar rol de admin
            cursor.execute("""
                INSERT IGNORE INTO usuarios_roles (id_usuario, id_rol)
                SELECT id_usuario, 1 FROM usuarios WHERE username = 'admin'
            """)
            
            print("    ✓ Usuario 'admin' creado")
            print(f"      📧 Email: admin@aguasrionegrinas.gov.ar")
            print(f"      👤 Username: admin")
            print(f"      🔑 Password: {password}")
            print(f"      📍 Localidad: Viedma")
            
            # ========================================
            # CATEGORÍAS INICIALES
            # ========================================
            print("\n  📁 Insertando categorías...")
            cursor.execute("""
                INSERT INTO categorias (tipo, nombre, codigo, descripcion) VALUES
                ('INSUMO', 'Químicos', 'QUIM', 'Productos químicos para tratamiento de agua'),
                ('INSUMO', 'Materiales de Construcción', 'CONST', 'Materiales para obras'),
                ('INSUMO', 'Herramientas', 'HERR', 'Herramientas de trabajo'),
                ('INSUMO', 'Repuestos', 'REP', 'Repuestos y piezas de equipos'),
                ('INSUMO', 'Equipos de Seguridad', 'SEG', 'Elementos de protección personal'),
                ('INSUMO', 'Oficina', 'OFIC', 'Materiales de oficina')
                ON DUPLICATE KEY UPDATE nombre=VALUES(nombre)
            """)
            print("    ✓ 6 categorías iniciales")
            
            # ========================================
            # LUGARES PARA VIEDMA (ejemplo)
            # ========================================
            print("\n  🏢 Insertando lugares de ejemplo...")
            cursor.execute("""
                INSERT INTO lugares (nombre, descripcion, tipo, id_localidad) VALUES
                ('Planta Potabilizadora Viedma', 'Planta de tratamiento de agua', 'planta', %s),
                ('Almacén Central Viedma', 'Depósito principal', 'almacen', %s),
                ('Taller Viedma', 'Taller de mantenimiento', 'servicio', %s)
                ON DUPLICATE KEY UPDATE nombre=VALUES(nombre)
            """, (id_viedma, id_viedma, id_viedma))
            print("    ✓ 3 lugares creados en Viedma")
            
        connection.commit()
        print("\n✅ Datos iniciales insertados correctamente")
        
    except Exception as e:
        connection.rollback()
        print(f"\n❌ Error al insertar datos iniciales: {e}")
        raise
    finally:
        connection.close()


def verify_installation():
    """Verificar que la instalación fue exitosa"""
    print("\n🔍 Verificando instalación...")
    
    config = DB_CONFIG.copy()
    config['database'] = DB_NAME
    connection = pymysql.connect(**config)
    
    try:
        with connection.cursor() as cursor:
            # Contar tablas
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM information_schema.tables 
                WHERE table_schema = %s
            """, (DB_NAME,))
            result = cursor.fetchone()
            print(f"  📊 Tablas creadas: {result[0]}")
            
            # Verificar datos
            cursor.execute("SELECT COUNT(*) as total FROM localidades")
            print(f"  📍 Localidades: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) as total FROM roles")
            print(f"  👥 Roles: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) as total FROM permisos")
            print(f"  🔐 Permisos: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            print(f"  👤 Usuarios: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) as total FROM categorias")
            print(f"  📁 Categorías: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) as total FROM lugares")
            print(f"  🏢 Lugares: {cursor.fetchone()[0]}")
            
            # Verificar permisos por rol
            print("\n  📋 Permisos por rol:")
            cursor.execute("""
                SELECT r.nombre, COUNT(rp.id_permiso) as permisos
                FROM roles r
                LEFT JOIN roles_permisos rp ON r.id_rol = rp.id_rol
                GROUP BY r.nombre
                ORDER BY r.nivel
            """)
            for row in cursor.fetchall():
                print(f"    - {row[0]}: {row[1]} permisos")
            
        print("\n✅ Instalación verificada correctamente")
        
    except Exception as e:
        print(f"\n❌ Error al verificar instalación: {e}")
        raise
    finally:
        connection.close()


def main():
    """Función principal de inicialización"""
    try:
        # Paso 1: Crear base de datos
        create_database()
        
        # Paso 2: Crear tablas
        create_tables()
        
        # Paso 3: Insertar datos iniciales
        insert_initial_data()
        
        # Paso 4: Verificar instalación
        verify_installation()
        
        print("\n" + "="*70)
        print("✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("="*70)
        print("\n📋 CREDENCIALES DE ACCESO:")
        print("   👤 Username: admin")
        print("   🔑 Password: comahue719")
        print("   📧 Email: admin@aguasrionegrinas.gov.ar")
        print("   📍 Localidad: Viedma")
        print("\n⚠️  IMPORTANTE: Cambiar la contraseña después del primer login")
        print("\n🌊 Sistema listo para Aguas Rionegrinas")
        print("   📍 8 Localidades de Río Negro configuradas")
        print("   👥 4 Roles jerárquicos creados")
        print("   🔐 27 Permisos configurados")
        print("\n🚀 Ejecuta 'python run.py' para iniciar el servidor")
        print("="*70 + "\n")
        
    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ ERROR EN LA INICIALIZACIÓN")
        print("="*70)
        print(f"\n{str(e)}\n")
        raise


if __name__ == '__main__':
    main()