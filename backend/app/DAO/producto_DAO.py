"""
DAO de Productos
Maneja todas las operaciones de base de datos relacionadas con productos
"""

from app.db.conexion_DB import ConectDB


class ProductoDAO:
    """Data Access Object para la tabla productos"""
    
    @staticmethod
    def create(data: dict) -> int:
        """
        Crear un nuevo producto
        
        Args:
            data (dict): {
                'nombre': str,
                'codigo': str,
                'descripcion': str,
                'id_categoria': int,
                'costo': float (opcional),
                'unidad_medida': str (opcional),
                'stock_minimo': int
            }
        
        Returns:
            int: ID del producto creado
        """
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO productos 
                    (nombre, codigo, descripcion, id_categoria, costo, unidad_medida, stock_minimo, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
                """
                cursor.execute(query, (
                    data['nombre'],
                    data.get('codigo'),
                    data.get('descripcion', ''),
                    data['id_categoria'],
                    data.get('costo'),
                    data.get('unidad_medida'),
                    data.get('stock_minimo', 0)
                ))
                connection.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating producto: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def get_stock_en_localidad(localidad_nombre: str) -> dict:
        """Obtener stock de todos los productos en una localidad"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor(dictionary=True) as cursor:
                query = """
                    SELECT p.id_producto, p.nombre, p.descripcion, COALESCE(SUM(pl.cantidad), 0) as stock
                    FROM productos p
                    INNER JOIN productos_localidad pl ON p.id_producto = pl.id_producto
                    INNER JOIN localidades l ON pl.id_localidad = l.id_localidad
                    WHERE l.nombre = %s and p.activo = 1
                    GROUP BY p.id_producto
                """
                cursor.execute(query, (localidad_nombre,))
                return {row['id_producto']: {'nombre': row['nombre'], 'descripcion': row['descripcion'], 'stock': row['stock']} for row in cursor.fetchall()}
        except Exception as e:
            print(f"Error getting stock en localidad: {e}")
            raise
        finally:
            connection.close()

    #creamos una funcion que registre localidad/producto
    @staticmethod
    def producto_localidad(data: dict) -> int:
        """
        Registrar un producto en una localidad específica
        
        Args:
            data (dict): {
                'id_producto': int,
                'id_localidad': int,
                'id_lugar': int,
                'cantidad': int
            }
        
        Returns:
            int: ID del registro creado
        """
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO productos_localidad 
                    (id_producto, id_localidad, id_lugar, cantidad)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (
                    data['id_producto'],
                    data['id_localidad'],
                    data['id_lugar'],
                    data['cantidad']
                ))
                connection.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating producto_localidad: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_all(page=1, limit=20, categoria_id=None, activo=None, search=None):
        """
        Obtener todos los productos con paginación y filtros
        
        Args:
            page (int): Número de página
            limit (int): Registros por página
            categoria_id (int): Filtrar por categoría
            activo (bool): Filtrar por activo
            search (str): Búsqueda por nombre o código
        
        Returns:
            dict: {'productos': list, 'pagination': dict}
        """
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                # Contar total
                count_query = """
                    SELECT COUNT(*) as total 
                    FROM productos p
                    WHERE 1=1
                """
                params = []
                
                if categoria_id:
                    count_query += " AND p.id_categoria = %s"
                    params.append(categoria_id)
                
                if activo is not None:
                    count_query += " AND p.activo = %s"
                    params.append(activo)
                
                if search:
                    count_query += " AND (p.nombre LIKE %s OR p.codigo LIKE %s)"
                    params.extend([f"%{search}%", f"%{search}%"])
                
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']
                
                # Obtener registros paginados
                offset = (page - 1) * limit
                query = """
                    SELECT p.*, c.nombre as categoria_nombre, c.codigo as categoria_codigo
                    FROM productos p
                    LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                    WHERE 1=1
                """
                
                if categoria_id:
                    query += " AND p.id_categoria = %s"
                
                if activo is not None:
                    query += " AND p.activo = %s"
                
                if search:
                    query += " AND (p.nombre LIKE %s OR p.codigo LIKE %s)"
                
                query += " ORDER BY p.id_producto DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                productos = cursor.fetchall()
                
                return {
                    'productos': productos,
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total': total,
                        'total_pages': (total + limit - 1) // limit
                    }
                }
        except Exception as e:
            print(f"Error getting productos: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(producto_id: int) -> dict:
        """Obtener un producto por ID"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor(dictionary=True) as cursor:
                query = """
                    SELECT p.*, c.nombre as categoria_nombre, c.codigo as categoria_codigo
                    FROM productos p
                    LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                    WHERE p.id_producto = %s
                """
                cursor.execute(query, (producto_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting producto by id: {e}")
            raise
        finally:
            connection.close()

    @staticmethod
    def get_by_codigo(codigo: str) -> dict:
        """Obtener un producto por código"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor(dictionary=True) as cursor:
                query = "SELECT * FROM productos WHERE codigo = %s"
                cursor.execute(query, (codigo,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting producto by codigo: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def update(producto_id: int, data: dict) -> bool:
        """Actualizar un producto"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                # Construir query dinámicamente
                fields = []
                values = []
                
                for key in ['nombre', 'codigo', 'descripcion', 'id_categoria', 
                           'costo', 'unidad_medida', 'stock_minimo', 'activo']:
                    if key in data:
                        fields.append(f"{key} = %s")
                        values.append(data[key])
                
                if not fields:
                    return False
                
                values.append(producto_id)
                query = f"UPDATE productos SET {', '.join(fields)} WHERE id_producto = %s"
                
                cursor.execute(query, values)
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating producto: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def delete(producto_id: int) -> bool:
        """Eliminar (soft delete) un producto"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = "UPDATE productos SET activo = 0 WHERE id_producto = %s"
                cursor.execute(query, (producto_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting producto: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def exists_codigo(codigo: str, id_producto: int = None) -> bool:
        """Verificar si existe un código de producto"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:

                query = "SELECT COUNT(*) as count FROM productos WHERE codigo = %s"
                params = [codigo]
                
                if id_producto:
                    query += " AND id_producto != %s"
                    params.append(id_producto)
                
                cursor.execute(query, params)
                result = cursor.fetchone()

                return result[0] > 0 # Cambiado de 'count' a índice 0 para evitar problemas con cursor sin dictionary=True

        except Exception as e:
            print(f"Error checking codigo: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_stock_total(producto_id: int) -> int:
        """Obtener stock total de un producto (suma de todas las localidades)"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT COALESCE(SUM(cantidad), 0) as stock_total
                    FROM productos_localidad
                    WHERE id_producto = %s
                """
                cursor.execute(query, (producto_id,))
                result = cursor.fetchone()
                return result['stock_total']
        except Exception as e:
            print(f"Error getting stock total: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_stock_por_localidad(producto_id: int) -> list:
        """Obtener stock de un producto por cada localidad"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT pl.*, 
                           loc.nombre as localidad_nombre,
                           lug.nombre as lugar_nombre,
                           lug.tipo as lugar_tipo
                    FROM productos_localidad pl
                    JOIN localidades loc ON pl.id_localidad = loc.id_localidad
                    JOIN lugares lug ON pl.id_lugar = lug.id_lugar
                    WHERE pl.id_producto = %s
                    ORDER BY loc.nombre, lug.nombre
                """
                cursor.execute(query, (producto_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting stock por localidad: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_stock_en_lugar(producto_id: int, lugar_id: int) -> int:
        """Obtener stock de un producto en un lugar específico"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT COALESCE(cantidad, 0) as cantidad
                    FROM productos_localidad
                    WHERE id_producto = %s AND id_lugar = %s
                """
                cursor.execute(query, (producto_id, lugar_id))
                result = cursor.fetchone()
                return result['cantidad'] if result else 0
        except Exception as e:
            print(f"Error getting stock en lugar: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_productos_stock_bajo() -> list:
        """Obtener productos con stock por debajo del mínimo"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT p.*, 
                           COALESCE(SUM(pl.cantidad), 0) as stock_total,
                           c.nombre as categoria_nombre
                    FROM productos p
                    LEFT JOIN productos_localidad pl ON p.id_producto = pl.id_producto
                    LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                    WHERE p.activo = 1
                    GROUP BY p.id_producto
                    HAVING stock_total < p.stock_minimo
                    ORDER BY p.nombre
                """
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting productos stock bajo: {e}")
            raise
        finally:
            connection.close()


    @staticmethod
    def exist_producto(nombre: str, id_categoria: int, id_localidad: int, id_lugar: int = None, id_producto: int = None) -> bool:

        """
            Verificar si existe un producto con el  nombre que tenga la categoría , dependiendo
            del lugar y localidad del usuario. 
        """
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT COUNT(*) 
                    FROM productos p
                    INNER JOIN categorias c ON p.id_categoria = c.id_categoria
                    INNER JOIN productos_localidad pl ON p.id_producto = pl.id_producto
                    INNER JOIN localidades l ON pl.id_localidad = l.id_localidad
                    INNER JOIN lugares lu ON pl.id_lugar = lu.id_lugar
                    WHERE p.nombre = %s        -- Nombre del producto
                    AND c.id_categoria = %s    -- ID de la categoría
                    AND l.id_localidad = %s    -- ID de la localidad (ej. Viedma)
                    AND lu.id_lugar = %s;      -- ID del lugar (ej. Almacén Central)
                """
                params = [nombre, id_categoria, id_localidad, id_lugar]
                
                if id_producto:
                    query += " AND id_producto != %s"
                    params.append(id_producto)
                
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] > 0 # Cambiado de 'count' a índice 0 para evitar problemas con cursor sin dictionary=True
        except Exception as e:
            print(f"Error checking nombre categoria: {e}")
            raise
        finally:
            connection.close()