"""
DAO de Usuarios
Maneja todas las operaciones de base de datos relacionadas con usuarios
"""

from app.db.conexion_DB import ConectDB


class UsuarioDAO:
    """Data Access Object para la tabla usuarios"""
    
    @staticmethod
    def create(data: dict) -> int:
        """
        Crear un nuevo usuario
        
        Args:
            data (dict): {
                'nombre': str,
                'apellido': str,
                'username': str,
                'email': str,
                'password_hash': str,
                'legajo': str (opcional),
                'id_localidad': int
            }
        
        Returns:
            int: ID del usuario creado o None si falla
        """
        try:
            with ConectDB.get_connection() as cursor:
                query = """
                    INSERT INTO usuarios 
                    (nombre, apellido, username, email, password_hash, legajo, id_localidad, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
                """
                cursor.execute(query, (
                    data['nombre'],
                    data['apellido'],
                    data['username'],
                    data.get('email'),
                    data['password_hash'],
                    data.get('legajo'),
                    data['id_localidad']
                ))
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating usuario: {e}")
            raise
    
    @staticmethod
    def get_all(page=1, limit=20, activo=None):
        """
        Obtener todos los usuarios con paginación
        
        Args:
            page (int): Número de página
            limit (int): Registros por página
            activo (bool): Filtrar por estado activo
        
        Returns:
            dict: {
                'usuarios': list,
                'pagination': {
                    'page': int,
                    'limit': int,
                    'total': int,
                    'total_pages': int
                }
            }
        """
        try:
            with ConectDB.get_connection() as cursor:
                # Contar total
                count_query = "SELECT COUNT(*) as total FROM usuarios WHERE 1=1"
                params = []
                
                if activo is not None:
                    count_query += " AND activo = %s"
                    params.append(activo)
                
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']
                
                # Obtener registros paginados
                offset = (page - 1) * limit
                query = """
                    SELECT u.*, l.nombre as localidad_nombre,
                           GROUP_CONCAT(r.nombre) as roles
                    FROM usuarios u
                    LEFT JOIN localidades l ON u.id_localidad = l.id_localidad
                    LEFT JOIN usuarios_roles ur ON u.id_usuario = ur.id_usuario
                    LEFT JOIN roles r ON ur.id_rol = r.id_rol
                    WHERE 1=1
                """
                
                if activo is not None:
                    query += " AND u.activo = %s"
                
                query += " GROUP BY u.id_usuario ORDER BY u.id_usuario DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                usuarios = cursor.fetchall()
                
                return {
                    'usuarios': usuarios,
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total': total,
                        'total_pages': (total + limit - 1) // limit
                    }
                }
        except Exception as e:
            print(f"Error getting usuarios: {e}")
            raise
    
    @staticmethod
    def get_by_id(usuario_id: int) -> dict:
        """
        Obtener un usuario por ID
        
        Args:
            usuario_id (int): ID del usuario
        
        Returns:
            dict: Datos del usuario o None
        """
        try:
            with ConectDB.get_connection() as cursor:
                query = """
                    SELECT u.*, l.nombre as localidad_nombre,
                           GROUP_CONCAT(r.nombre) as roles
                    FROM usuarios u
                    LEFT JOIN localidades l ON u.id_localidad = l.id_localidad
                    LEFT JOIN usuarios_roles ur ON u.id_usuario = ur.id_usuario
                    LEFT JOIN roles r ON ur.id_rol = r.id_rol
                    WHERE u.id_usuario = %s
                    GROUP BY u.id_usuario
                """
                cursor.execute(query, (usuario_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting usuario by id: {e}")
            raise
    
    @staticmethod
    def get_by_username(username: str) -> dict:
        connection = ConectDB.get_connection()
        with connection.cursor(dictionary=True) as cursor:
            try:
                query = """
                SELECT u.*, l.nombre as localidad_nombre,
                       GROUP_CONCAT(r.nombre) as roles,
                       GROUP_CONCAT(r.id_rol) as roles_ids
                FROM usuarios u
                LEFT JOIN localidades l ON u.id_localidad = l.id_localidad
                LEFT JOIN usuarios_roles ur ON u.id_usuario = ur.id_usuario
                LEFT JOIN roles r ON ur.id_rol = r.id_rol
                WHERE u.username = %s
                GROUP BY u.id_usuario
                """
                cursor.execute(query, (username,))
                return cursor.fetchone()
            except Exception as e:
                print(f"Error getting usuario by username: {e}")
                raise
            finally:
                connection.close()
    
    @staticmethod
    def get_by_email(email: str) -> dict:
        """Obtener usuario por email"""
        try:
            with ConectDB.get_connection() as cursor:
                query = "SELECT * FROM usuarios WHERE email = %s"
                cursor.execute(query, (email,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting usuario by email: {e}")
            raise
    
    @staticmethod
    def update(usuario_id: int, data: dict) -> bool:
        """
        Actualizar un usuario
        
        Args:
            usuario_id (int): ID del usuario
            data (dict): Datos a actualizar
        
        Returns:
            bool: True si se actualizó, False si no
        """
        try:
            with ConectDB.get_connection() as cursor:
                # Construir query dinámicamente
                fields = []
                values = []
                
                for key in ['nombre', 'apellido', 'email', 'legajo', 'id_localidad', 'activo']:
                    if key in data:
                        fields.append(f"{key} = %s")
                        values.append(data[key])
                
                if not fields:
                    return False
                
                values.append(usuario_id)
                query = f"UPDATE usuarios SET {', '.join(fields)} WHERE id_usuario = %s"
                
                cursor.execute(query, values)
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating usuario: {e}")
            raise
    
    @staticmethod
    def update_password(usuario_id: int, password_hash: str) -> bool:
        """Actualizar contraseña de usuario"""
        try:
            with ConectDB.get_connection() as cursor:
                query = "UPDATE usuarios SET password_hash = %s WHERE id_usuario = %s"
                cursor.execute(query, (password_hash, usuario_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating password: {e}")
            raise
    
    @staticmethod
    def update_ultimo_login(usuario_id: int) -> bool:
        """Actualizar fecha de último login"""
        try:
            with ConectDB.get_connection() as cursor:
                query = "UPDATE usuarios SET ultimo_login = NOW() WHERE id_usuario = %s"
                cursor.execute(query, (usuario_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating ultimo_login: {e}")
            raise
    
    @staticmethod
    def delete(usuario_id: int) -> bool:
        """
        Eliminar (soft delete) un usuario
        
        Args:
            usuario_id (int): ID del usuario
        
        Returns:
            bool: True si se eliminó, False si no
        """
        try:
            with ConectDB.get_connection() as cursor:
                query = "UPDATE usuarios SET activo = 0 WHERE id_usuario = %s"
                cursor.execute(query, (usuario_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting usuario: {e}")
            raise
    
    @staticmethod
    def exists_username(username: str) -> bool:
        """Verificar si existe un username"""
        try:
            with ConectDB.get_connection() as cursor:
                query = "SELECT COUNT(*) as count FROM usuarios WHERE username = %s"
                cursor.execute(query, (username,))
                result = cursor.fetchone()
                return result['count'] > 0
        except Exception as e:
            print(f"Error checking username: {e}")
            raise
    
    @staticmethod
    def exists_email(email: str) -> bool:
        """Verificar si existe un email"""
        try:
            with ConectDB.get_connection() as cursor:
                query = "SELECT COUNT(*) as count FROM usuarios WHERE email = %s"
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                return result['count'] > 0
        except Exception as e:
            print(f"Error checking email: {e}")
            raise
    
    @staticmethod
    def asignar_rol(usuario_id: int, rol_id: int, asignado_por: int = None) -> bool:
        """Asignar un rol a un usuario"""
        try:
            with ConectDB.get_connection() as cursor:
                query = """
                    INSERT INTO usuarios_roles (id_usuario, id_rol, asignado_por)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (usuario_id, rol_id, asignado_por))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error asignando rol: {e}")
            raise
    
    @staticmethod
    def quitar_rol(usuario_id: int, rol_id: int) -> bool:
        """Quitar un rol de un usuario"""
        try:
            with ConectDB.get_connection() as cursor:
                query = "DELETE FROM usuarios_roles WHERE id_usuario = %s AND id_rol = %s"
                cursor.execute(query, (usuario_id, rol_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error quitando rol: {e}")
            raise
    
    @staticmethod
    def get_permisos(usuario_id: int) -> list:
        """Obtener todos los permisos de un usuario"""
        try:
            with ConectDB.get_connection() as cursor:
                query = """
                    SELECT DISTINCT p.nombre, p.descripcion, p.recurso
                    FROM usuarios_roles ur
                    JOIN roles_permisos rp ON ur.id_rol = rp.id_rol
                    JOIN permisos p ON rp.id_permiso = p.id_permiso
                    WHERE ur.id_usuario = %s
                    ORDER BY p.recurso, p.nombre
                """
                cursor.execute(query, (usuario_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting permisos: {e}")
            raise
    
    @staticmethod
    def tiene_permiso(usuario_id: int, nombre_permiso: str) -> bool:
        """Verificar si un usuario tiene un permiso específico"""
        try:
            with ConectDB.get_connection() as cursor:
                query = """
                    SELECT COUNT(*) as count
                    FROM usuarios_roles ur
                    JOIN roles_permisos rp ON ur.id_rol = rp.id_rol
                    JOIN permisos p ON rp.id_permiso = p.id_permiso
                    WHERE ur.id_usuario = %s AND p.nombre = %s
                """
                cursor.execute(query, (usuario_id, nombre_permiso))
                result = cursor.fetchone()
                return result['count'] > 0
        except Exception as e:
            print(f"Error checking permiso: {e}")
            raise