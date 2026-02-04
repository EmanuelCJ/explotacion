"""
DAO de Lugares
Maneja operaciones de lugares físicos dentro de localidades
"""

from app.db.conexion_DB import ConectDB


class LugarDAO:
    """Data Access Object para la tabla lugares"""
    
    @staticmethod
    def create(data: dict) -> int:
        """
        Crear un nuevo lugar
        
        Args:
            data (dict): {
                'nombre': str,
                'descripcion': str,
                'tipo': str (servicio, planta, almacen, deposito, otro),
                'id_localidad': int
            }
        """
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO lugares 
                    (nombre, descripcion, tipo, id_localidad, activo)
                    VALUES (%s, %s, %s, %s, 1)
                """
                cursor.execute(query, (
                    data['nombre'],
                    data.get('descripcion', ''),
                    data.get('tipo', 'almacen'),
                    data['id_localidad']
                ))
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating lugar: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_all(localidad_id=None, tipo=None, activo=None):
        """Obtener todos los lugares con filtros"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT l.*, loc.nombre as localidad_nombre, loc.ciudad
                    FROM lugares l
                    JOIN localidades loc ON l.id_localidad = loc.id_localidad
                    WHERE 1=1
                """
                params = []
                
                if localidad_id:
                    query += " AND l.id_localidad = %s"
                    params.append(localidad_id)
                
                if tipo:
                    query += " AND l.tipo = %s"
                    params.append(tipo)
                
                if activo is not None:
                    query += " AND l.activo = %s"
                    params.append(activo)
                
                query += " ORDER BY loc.nombre, l.nombre"
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting lugares: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(lugar_id: int) -> dict:
        """Obtener lugar por ID"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT l.*, loc.nombre as localidad_nombre
                    FROM lugares l
                    JOIN localidades loc ON l.id_localidad = loc.id_localidad
                    WHERE l.id_lugar = %s
                """
                cursor.execute(query, (lugar_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting lugar by id: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_by_localidad(localidad_id: int, activo=True) -> list:
        """Obtener todos los lugares de una localidad"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM lugares WHERE id_localidad = %s"
                params = [localidad_id]
                
                if activo is not None:
                    query += " AND activo = %s"
                    params.append(activo)
                
                query += " ORDER BY tipo, nombre"
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting lugares by localidad: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def update(lugar_id: int, data: dict) -> bool:
        """Actualizar lugar"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                fields = []
                values = []
                
                for key in ['nombre', 'descripcion', 'tipo', 'id_localidad', 'activo']:
                    if key in data:
                        fields.append(f"{key} = %s")
                        values.append(data[key])
                
                if not fields:
                    return False
                
                values.append(lugar_id)
                query = f"UPDATE lugares SET {', '.join(fields)} WHERE id_lugar = %s"
                cursor.execute(query, values)
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating lugar: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def delete(lugar_id: int) -> bool:
        """Eliminar (soft delete) lugar"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "UPDATE lugares SET activo = 0 WHERE id_lugar = %s"
                cursor.execute(query, (lugar_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting lugar: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_stock_en_lugar(lugar_id: int) -> list:
        """Obtener todos los productos con stock en un lugar"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT pl.*, p.nombre as producto_nombre, p.codigo as producto_codigo
                    FROM productos_localidad pl
                    JOIN productos p ON pl.id_producto = p.id_producto
                    WHERE pl.id_lugar = %s AND pl.cantidad > 0
                    ORDER BY p.nombre
                """
                cursor.execute(query, (lugar_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting stock en lugar: {e}")
            raise
        finally:
            connection.close()