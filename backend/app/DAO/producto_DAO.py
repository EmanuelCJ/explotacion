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
            with ConectDB.get_cursor() as cursor:
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
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating producto: {e}")
            raise
    
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
            with ConectDB.get_cursor() as cursor:
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
    
    @staticmethod
    def get_by_id(producto_id: int) -> dict:
        """Obtener un producto por ID"""
        try:
            with ConectDB.get_cursor() as cursor:
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
    
    @staticmethod
    def get_by_codigo(codigo: str) -> dict:
        """Obtener un producto por código"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = "SELECT * FROM productos WHERE codigo = %s"
                cursor.execute(query, (codigo,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting producto by codigo: {e}")
            raise
    
    @staticmethod
    def update(producto_id: int, data: dict) -> bool:
        """Actualizar un producto"""
        try:
            with ConectDB.get_cursor() as cursor:
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
            raise
    
    @staticmethod
    def delete(producto_id: int) -> bool:
        """Eliminar (soft delete) un producto"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = "UPDATE productos SET activo = 0 WHERE id_producto = %s"
                cursor.execute(query, (producto_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting producto: {e}")
            raise
    
    @staticmethod
    def exists_codigo(codigo: str, exclude_id: int = None) -> bool:
        """Verificar si existe un código de producto"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = "SELECT COUNT(*) as count FROM productos WHERE codigo = %s"
                params = [codigo]
                
                if exclude_id:
                    query += " AND id_producto != %s"
                    params.append(exclude_id)
                
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result['count'] > 0
        except Exception as e:
            print(f"Error checking codigo: {e}")
            raise
    
    @staticmethod
    def get_stock_total(producto_id: int) -> int:
        """Obtener stock total de un producto (suma de todas las localidades)"""
        try:
            with ConectDB.get_cursor() as cursor:
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
    
    @staticmethod
    def get_stock_por_localidad(producto_id: int) -> list:
        """Obtener stock de un producto por cada localidad"""
        try:
            with ConectDB.get_cursor() as cursor:
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
    
    @staticmethod
    def get_stock_en_lugar(producto_id: int, lugar_id: int) -> int:
        """Obtener stock de un producto en un lugar específico"""
        try:
            with ConectDB.get_cursor() as cursor:
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
    
    @staticmethod
    def get_productos_stock_bajo() -> list:
        """Obtener productos con stock por debajo del mínimo"""
        try:
            with ConectDB.get_cursor() as cursor:
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