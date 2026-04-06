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
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
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
                connection.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating usuario: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_all(page=1, limit=20, activo=None) -> dict:
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
            connection = ConectDB.get_connection()
            with connection.cursor(dictionary=True) as cursor:
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
                    SELECT u.id_usuario, 
                    u.nombre, 
                    u.email, 
                    u.apellido,
                    u.legajo,
                    u.activo,
                    u.created_at, l.nombre as localidad_nombre,
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
        finally:
            connection.close()
    
    @staticmethod
    def get_all_sin_paginacion() -> dict:
        """
        Obtener todos los usuarios sin paginación
        
        Returns:
            dict: {
                'usuarios': list
            }
        """
        try:
            connection = ConectDB.get_connection()
            with connection.cursor(dictionary=True) as cursor:
                query = """
                    SELECT u.id_usuario, 
                    u.id_usuario,
                    u.username,
                    u.nombre, 
                    u.apellido,
                    u.activo,
                    u.legajo,
                    u.email,
                    u.created_at,
                    u.updated_at, l.nombre as localidad_nombre,
                           GROUP_CONCAT(r.nombre) as roles
                    FROM usuarios u
                    LEFT JOIN localidades l ON u.id_localidad = l.id_localidad
                    LEFT JOIN usuarios_roles ur ON u.id_usuario = ur.id_usuario
                    LEFT JOIN roles r ON ur.id_rol = r.id_rol
                    GROUP BY u.id_usuario ORDER BY u.id_usuario DESC
                """
                cursor.execute(query)
                usuarios = cursor.fetchall()
                
                return {
                    'usuarios': usuarios
                }
        except Exception as e:
            print(f"Error getting usuarios: {e}")
            raise
        finally:
            connection.close()


    @staticmethod
    def get_id(usuario_id: int) -> dict:
        """
        Obtener un usuario por ID
        
        Args:
            usuario_id (int): ID del usuario
        
        Returns:
            dict: Datos del usuario o None
        """
        try:
            connection = ConectDB.get_connection()
            with connection.cursor(dictionary=True) as cursor:
                query = """
                    SELECT 
                    u.id_usuario,
                    u.username,
                    u.nombre, 
                    u.apellido,
                    u.activo,
                    u.legajo,
                    u.email,
                    u.created_at,
                    u.updated_at,
                    l.nombre AS localidad_nombre,
                    GROUP_CONCAT(r.nombre) AS roles
                    FROM usuarios u
                    LEFT JOIN localidades l ON u.id_localidad = l.id_localidad
                    LEFT JOIN usuarios_roles ur ON u.id_usuario = ur.id_usuario
                    LEFT JOIN roles r ON ur.id_rol = r.id_rol
                    WHERE u.id_usuario = %s
                    GROUP BY u.id_usuario;
                """
                cursor.execute(query, (usuario_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting usuario by id: {e}")
            raise
        finally:
            connection.close()

    @staticmethod
    def get_by_id(usuario_id: int) -> dict:
        """
        Obtener un usuario por ID incluyendo password_hash para el refresh token
        
        Args:
            usuario_id (int): ID del usuario
        
        Returns:
            dict: Datos del usuario o None
        """
        try:
            connection = ConectDB.get_connection()
            with connection.cursor(dictionary=True) as cursor:
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
        finally:
            connection.close()
        
    @staticmethod
    def username(usuario_id: int) -> dict:
        """
        Obtener un usuario por username
        
        Args:
            usuario_id (int): ID del usuario
        
        Returns:
            dict: Username del usuario o None
        """
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT username
                    FROM usuarios
                    WHERE id_usuario = %s;
                """
                cursor.execute(query, (usuario_id,))
                result = cursor.fetchone()
                return result[0] if result else None
            
        except Exception as e:
            print(f"Error getting usuario by id: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_by_username(username: str) -> dict:
        """Obtener usuario por nombre de usuario"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor(dictionary=True) as cursor:
                query = """
                SELECT 
                    u.*
                , l.nombre as localidad_nombre,
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
                row = cursor.fetchone()
                return row
        except Exception as e:
                print(f"Error getting usuario by username: {e}")
                raise
        finally:
                connection.close()
    
    
    @staticmethod
    def get_by_email(email: str) -> dict:
        """Obtener usuario por email"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM usuarios WHERE email = %s"
                cursor.execute(query, (email,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting usuario by email: {e}")
            raise
        finally:
            connection.close()
    
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
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
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
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def update_password(usuario_id: int, password_hash: str) -> bool:
        """Actualizar contraseña de usuario"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "UPDATE usuarios SET password_hash = %s WHERE id_usuario = %s"
                cursor.execute(query, (password_hash, usuario_id))
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating password: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def update_ultimo_login(usuario_id: int) -> bool:
        """Actualizar fecha de último login"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "UPDATE usuarios SET ultimo_login = NOW() WHERE id_usuario = %s"
                cursor.execute(query, (usuario_id,))
                respuesta = cursor.rowcount > 0
                return respuesta
        except Exception as e:
                print(f"Error updating ultimo_login: {e}")
                connection.rollback()
                raise
        finally:
                connection.close()
    
    # Esta funcion no debe estar por que el id del usuario tiene relacion con tabla auditoria.
    # @staticmethod
    # def delete(usuario_id: int) -> bool:
    #     """
    #     Eliminar (soft delete) un usuario
        
    #     Args:
    #         usuario_id (int): ID del usuario
        
    #     Returns:
    #         bool: True si se eliminó, False si no
    #     """
    #     try:
    #         connection = ConectDB.get_connection()
    #         with connection.cursor() as cursor:
    #             query = "DELETE FROM usuarios WHERE id_usuario = %s"
    #             cursor.execute(query, (usuario_id,))
    #             connection.commit()
    #             return cursor.rowcount > 0
    #     except Exception as e:
    #         print(f"Error deleting usuario: {e}")
    #         connection.rollback()
    #         raise
    #     finally:
    #         connection.close()
    
    @staticmethod
    def exists_username(username: str) -> bool:
        """Verificar si existe un username"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT COUNT(*) as count FROM usuarios WHERE username = %s"
                cursor.execute(query, (username,))
                result = cursor.fetchone()
                return result[0] > 0
        except Exception as e:
            print(f"Error checking username: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def exists_email(email: str) -> bool:
        """Verificar si existe un email"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT COUNT(*) as count FROM usuarios WHERE email = %s"
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                return result[0] > 0
        except Exception as e:
            print(f"Error checking email: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def asignar_rol(usuario_id: int, rol_id: int, asignado_por: int = None) -> bool:

        """Asignar un rol a un usuario"""

        # validar roles posibles para asignar, no se pueden asignar roles que no existan en la tabla roles
        if not UsuarioDAO.rol_existe(rol_id):
            raise ValueError(f"El rol con ID {rol_id} no existe")

        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO usuarios_roles (id_usuario, id_rol, asignado_por)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    id_rol = VALUES(id_rol),
                    asignado_por = VALUES(asignado_por),
                    fecha_asignacion = CURRENT_TIMESTAMP
                """
                cursor.execute(query, (usuario_id, rol_id, asignado_por,))
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error asignando rol: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def quitar_rol(usuario_id: int) -> bool:
        
        """Quitar un rol de un usuario"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "DELETE FROM usuarios_roles WHERE id_usuario = %s"
                cursor.execute(query, (usuario_id,))
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error quitando rol: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def get_permisos(usuario_id: int) -> dict:
        """Obtener todos los permisos de un usuario"""
        
        try:
            connection = ConectDB.get_connection()
            with connection.cursor(dictionary=True) as cursor:
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
        finally:
            connection.close()
    
    @staticmethod
    def tiene_permiso(usuario_id: int, nombre_permiso: str) -> bool:
        """Verificar si un usuario tiene un permiso específico"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT COUNT(*) as count
                    FROM usuarios_roles ur
                    JOIN roles_permisos rp ON ur.id_rol = rp.id_rol
                    JOIN permisos p ON rp.id_permiso = p.id_permiso
                    WHERE ur.id_usuario = %s AND p.nombre = %s
                """
                cursor.execute(query, (usuario_id, nombre_permiso))
                result = cursor.fetchone()
                return result[0] > 0 
        except Exception as e:
            print(f"Error checking permiso : {e}")
            raise
        finally:
            connection.close()

    @staticmethod
    def get_rol(usuario_id: int) -> dict:
        """Obtener el rol principal de un usuario"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT r.nombre
                    FROM usuarios_roles ur
                    JOIN roles r ON ur.id_rol = r.id_rol
                    WHERE ur.id_usuario = %s
                    ORDER BY ur.asignado_por DESC
                    LIMIT 1
                """
                cursor.execute(query, (usuario_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error getting rol: {e}")
            raise
        finally:
            connection.close()

    
    @staticmethod
    def rol_existe(rol_id: int) -> bool:
        """Verificar si existe un rol por ID"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT COUNT(*) as count FROM roles WHERE id_rol = %s"
                cursor.execute(query, (rol_id,))
                result = cursor.fetchone()
                return result[0] > 0
        except Exception as e:
            print(f"Error checking rol: {e}")
            raise
        finally:
            connection.close()


    @staticmethod
    def activar_usuario(usuario_id: int) -> bool:
        """Activar un usuario"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "UPDATE usuarios SET activo = 1 WHERE id_usuario = %s"
                cursor.execute(query, (usuario_id,))
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error activating usuario: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def desactivar_usuario(usuario_id: int) -> bool:
        """Desactivar un usuario"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "UPDATE usuarios SET activo = 0 WHERE id_usuario = %s"
                cursor.execute(query, (usuario_id,))
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error desactivating usuario: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def get_estado(usuario_id: int) -> bool:
        """Obtener el estado activo de un usuario"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT activo FROM usuarios WHERE id_usuario = %s"
                cursor.execute(query, (usuario_id,))
                result = cursor.fetchone()
                return result[0] == 1 if result else False
        except Exception as e:
            print(f"Error getting estado: {e}")
            raise
        finally:
            connection.close()

    # esta funcion deberia recibir un diccionario con los datos que se desean actualiar por editor
    @staticmethod
    def update_usuario(id_usuario: int, data: dict) -> bool:

        """
        
            Actualizar un usuario con datos dinámicos
            crea una query UPDATE dinámicamente según los campos presentes en el diccionario data
            dependiendo los datos se envian desde el frontend

        """
        
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:

                # Validar campos permitidos
                campos_permitidos = ['nombre', 'apellido', 'username', 'email', 'legajo', 'id_localidad', 'activo']
                for key in data.keys():
                 if key not in campos_permitidos:
                    raise ValueError(f"Campo no permitido para actualizar: {key}")
    
                # Validar que haya al menos un campo
                if not data:
                    raise ValueError("No se proporcionaron campos para actualizar")
                
                # Construir la parte SET de la query dinámicamente
                # Ejemplo: "nombre=%s, apellido=%s, rol=%s"
                set_clause = ", ".join([f"{campo}=%s" for campo in data.keys()])
            
                # Query completa
                query = f"""
                    UPDATE usuarios
                    SET {set_clause}
                    WHERE id_usuario=%s
                """
            
                # Los valores en el orden correcto
                values = tuple(data.values()) + (id_usuario,)
            
                cursor.execute(query, values)
                connection.commit()
            
                return cursor.rowcount > 0  # True si actualizó al menos 1 fila
            
        except Exception as e:
                connection.rollback()
                print(f"Error update usuarioDAO: {e}")
                return False
        finally:
                connection.close()
        
    @staticmethod
    def get_localidad(localidad_id: int) -> dict:
        """Obtener localidad de un usuario"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor(dictionary=True) as cursor:
                query = """
                        SELECT 
                        u.id_usuario, 
                        u.nombre, 
                        u.email, 
                        l.nombre AS localidad_nombre
                        FROM usuarios u
                        INNER JOIN localidades l ON u.id_localidad = l.id_localidad
                WHERE l.id_localidad = %s;
                """
                
                cursor.execute(query, (localidad_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting localidad: {e}")
            raise
        finally:
            connection.close()