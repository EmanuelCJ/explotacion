"""
DAO de Categorías
Maneja operaciones de base de datos para categorías de productos
"""

from app.db.conexion_DB import ConectDB


class CategoriaDAO:
    """Data Access Object para la tabla categorias"""
    
    @staticmethod
    def create(data: dict) -> int:
        """
        Crear una nueva categoría
        
        Args:
            data (dict): {
                'tipo': str,
                'nombre': str,
                'codigo': str,
                'descripcion': str
            }
        """
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO categorias 
                    (tipo, nombre, codigo, descripcion, activo)
                    VALUES (%s, %s, %s, %s, 1)
                """
                cursor.execute(query, (
                    data['tipo'],
                    data['nombre'],
                    data.get('codigo'),
                    data.get('descripcion', '')
                ))
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating categoria: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_all(activo=None):
        """Obtener todas las categorías"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM categorias WHERE 1=1"
                params = []
                
                if activo is not None:
                    query += " AND activo = %s"
                    params.append(activo)
                
                query += " ORDER BY tipo, nombre"
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting categorias: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(categoria_id: int) -> dict:
        """Obtener categoría por ID"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM categorias WHERE id_categoria = %s"
                cursor.execute(query, (categoria_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting categoria by id: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_by_codigo(codigo: str) -> dict:
        """Obtener categoría por código"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM categorias WHERE codigo = %s"
                cursor.execute(query, (codigo,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting categoria by codigo: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_by_tipo(tipo: str) -> list:
        """Obtener categorías por tipo"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM categorias WHERE tipo = %s AND activo = 1 ORDER BY nombre"
                cursor.execute(query, (tipo,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting categorias by tipo: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def update(categoria_id: int, data: dict) -> bool:
        """Actualizar categoría"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                fields = []
                values = []
                
                for key in ['tipo', 'nombre', 'codigo', 'descripcion', 'activo']:
                    if key in data:
                        fields.append(f"{key} = %s")
                        values.append(data[key])
                
                if not fields:
                    return False
                
                values.append(categoria_id)
                query = f"UPDATE categorias SET {', '.join(fields)} WHERE id_categoria = %s"
                cursor.execute(query, values)
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating categoria: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def delete(categoria_id: int) -> bool:
        """Eliminar (soft delete) categoría"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "UPDATE categorias SET activo = 0 WHERE id_categoria = %s"
                cursor.execute(query, (categoria_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting categoria: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def exists_codigo(codigo: str, exclude_id: int = None) -> bool:
        """Verificar si existe una categoría con ese código"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT COUNT(*) as count FROM categorias WHERE codigo = %s"
                params = [codigo]
                
                if exclude_id:
                    query += " AND id_categoria != %s"
                    params.append(exclude_id)
                
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result['count'] > 0
        except Exception as e:
            print(f"Error checking codigo: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def count_productos(categoria_id: int) -> int:
        """Contar productos de una categoría"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT COUNT(*) as count 
                    FROM productos 
                    WHERE id_categoria = %s AND activo = 1
                """
                cursor.execute(query, (categoria_id,))
                result = cursor.fetchone()
                return result['count']
        except Exception as e:
            print(f"Error counting productos: {e}")
            raise
        finally:
            connection.close()