"""
DAO de Roles y Permisos
Maneja roles y permisos del sistema
"""

from app.db.conexion_DB import ConectDB


class RolDAO:
    """Data Access Object para la tabla roles"""
    
    @staticmethod
    def get_all(activo=None) -> list:
        """Obtener todos los roles"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM roles WHERE 1=1"
                params = []
                
                if activo is not None:
                    query += " AND activo = %s"
                    params.append(activo)
                
                query += " ORDER BY nivel"
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting roles: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(rol_id: int) -> dict:
        """Obtener un rol por ID"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM roles WHERE id_rol = %s"
                cursor.execute(query, (rol_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting rol by id: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_by_nombre(nombre: str) -> dict:
        """Obtener un rol por nombre"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM roles WHERE nombre = %s"
                cursor.execute(query, (nombre,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting rol by nombre: {e}")
            raise
        finally:
            connection.close()

    @staticmethod
    def get_permisos(rol_id: int) -> list:
        """Obtener todos los permisos de un rol"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT p.*
                    FROM roles_permisos rp
                    JOIN permisos p ON rp.id_permiso = p.id_permiso
                    WHERE rp.id_rol = %s
                    ORDER BY p.recurso, p.nombre
                """
                cursor.execute(query, (rol_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting permisos de rol: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def asignar_permiso(rol_id: int, permiso_id: int) -> bool:
        """Asignar un permiso a un rol"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    INSERT IGNORE INTO roles_permisos (id_rol, id_permiso)
                    VALUES (%s, %s)
                """
                cursor.execute(query, (rol_id, permiso_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error asignando permiso: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def quitar_permiso(rol_id: int, permiso_id: int) -> bool:
        """Quitar un permiso de un rol"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "DELETE FROM roles_permisos WHERE id_rol = %s AND id_permiso = %s"
                cursor.execute(query, (rol_id, permiso_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error quitando permiso: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def count_usuarios(rol_id: int) -> int:
        """Contar usuarios con este rol"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT COUNT(*) as count FROM usuarios_roles WHERE id_rol = %s"
                cursor.execute(query, (rol_id,))
                result = cursor.fetchone()
                return result['count']
        except Exception as e:
            print(f"Error counting usuarios: {e}")
            raise
        finally:
            connection.close()


class PermisoDAO:
    """Data Access Object para la tabla permisos"""
    
    @staticmethod
    def get_all() -> list:
        """Obtener todos los permisos"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM permisos ORDER BY recurso, nombre"
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting permisos: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(permiso_id: int) -> dict:
        """Obtener un permiso por ID"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM permisos WHERE id_permiso = %s"
                cursor.execute(query, (permiso_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting permiso by id: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_by_nombre(nombre: str) -> dict:
        """Obtener un permiso por nombre"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor(dictionary=True) as cursor:
                query = "SELECT * FROM permisos WHERE nombre = %s"
                cursor.execute(query, (nombre,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting permiso by nombre: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_by_recurso(recurso: str) -> list:
        """Obtener todos los permisos de un recurso"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM permisos WHERE recurso = %s ORDER BY nombre"
                cursor.execute(query, (recurso,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting permisos by recurso: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_recursos() -> list:
        """Obtener lista de recursos únicos"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT DISTINCT recurso FROM permisos ORDER BY recurso"
                cursor.execute(query)
                return [row['recurso'] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting recursos: {e}")
            raise
        finally:
            connection.close()