"""
DAO de Localidades
Maneja operaciones de base de datos para localidades de Río Negro
"""

from app.db.conexion_DB import ConectDB


class LocalidadDAO:
    """Data Access Object para la tabla localidades"""
    
    @staticmethod
    def create(data: dict) -> int:
        """
        Crear una nueva localidad
        
        Args:
            data (dict): {
                'nombre': str,
                'descripcion': str,
                'direccion': str,
                'ciudad': str,
                'codigo_postal': str
            }
        """
        try:
            with ConectDB.get_cursor() as cursor:
                query = """
                    INSERT INTO localidades 
                    (nombre, descripcion, direccion, ciudad, codigo_postal, activo)
                    VALUES (%s, %s, %s, %s, %s, 1)
                """
                cursor.execute(query, (
                    data['nombre'],
                    data.get('descripcion', ''),
                    data.get('direccion', ''),
                    data.get('ciudad', ''),
                    data.get('codigo_postal', '')
                ))
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating localidad: {e}")
            raise
    
    @staticmethod
    def get_all(activo=None):
        """Obtener todas las localidades"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = "SELECT * FROM localidades WHERE 1=1"
                params = []
                
                if activo is not None:
                    query += " AND activo = %s"
                    params.append(activo)
                
                query += " ORDER BY nombre"
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting localidades: {e}")
            raise
    
    @staticmethod
    def get_by_id(localidad_id: int) -> dict:
        """Obtener localidad por ID"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = "SELECT * FROM localidades WHERE id_localidad = %s"
                cursor.execute(query, (localidad_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting localidad by id: {e}")
            raise
    
    @staticmethod
    def get_by_nombre(nombre: str) -> dict:
        """Obtener localidad por nombre"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = "SELECT * FROM localidades WHERE nombre = %s"
                cursor.execute(query, (nombre,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting localidad by nombre: {e}")
            raise
    
    @staticmethod
    def get_con_lugares(localidad_id: int) -> dict:
        """Obtener localidad con sus lugares"""
        try:
            with ConectDB.get_cursor() as cursor:
                # Obtener localidad
                query_loc = "SELECT * FROM localidades WHERE id_localidad = %s"
                cursor.execute(query_loc, (localidad_id,))
                localidad = cursor.fetchone()
                
                if not localidad:
                    return None
                
                # Obtener lugares de esta localidad
                query_lugares = """
                    SELECT * FROM lugares 
                    WHERE id_localidad = %s AND activo = 1
                    ORDER BY nombre
                """
                cursor.execute(query_lugares, (localidad_id,))
                localidad['lugares'] = cursor.fetchall()
                
                return localidad
        except Exception as e:
            print(f"Error getting localidad con lugares: {e}")
            raise
    
    @staticmethod
    def update(localidad_id: int, data: dict) -> bool:
        """Actualizar localidad"""
        try:
            with ConectDB.get_cursor() as cursor:
                fields = []
                values = []
                
                for key in ['nombre', 'descripcion', 'direccion', 'ciudad', 'codigo_postal', 'activo']:
                    if key in data:
                        fields.append(f"{key} = %s")
                        values.append(data[key])
                
                if not fields:
                    return False
                
                values.append(localidad_id)
                query = f"UPDATE localidades SET {', '.join(fields)} WHERE id_localidad = %s"
                cursor.execute(query, values)
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating localidad: {e}")
            raise
    
    @staticmethod
    def delete(localidad_id: int) -> bool:
        """Eliminar (soft delete) localidad"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = "UPDATE localidades SET activo = 0 WHERE id_localidad = %s"
                cursor.execute(query, (localidad_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting localidad: {e}")
            raise
    
    @staticmethod
    def exists_nombre(nombre: str, exclude_id: int = None) -> bool:
        """Verificar si existe una localidad con ese nombre"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = "SELECT COUNT(*) as count FROM localidades WHERE nombre = %s"
                params = [nombre]
                
                if exclude_id:
                    query += " AND id_localidad != %s"
                    params.append(exclude_id)
                
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result['count'] > 0
        except Exception as e:
            print(f"Error checking nombre: {e}")
            raise
    
    @staticmethod
    def count_lugares(localidad_id: int) -> int:
        """Contar lugares de una localidad"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = """
                    SELECT COUNT(*) as count 
                    FROM lugares 
                    WHERE id_localidad = %s AND activo = 1
                """
                cursor.execute(query, (localidad_id,))
                result = cursor.fetchone()
                return result['count']
        except Exception as e:
            print(f"Error counting lugares: {e}")
            raise