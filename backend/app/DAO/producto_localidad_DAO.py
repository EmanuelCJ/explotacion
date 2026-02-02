"""
DAO de Producto-Localidad
Maneja el stock de productos en cada lugar de cada localidad
ESTE ES CRÍTICO - Actualiza el stock físico
"""

from app.db.conexion_DB import ConectDB


class ProductoLocalidadDAO:
    """Data Access Object para la tabla productos_localidad"""
    
    @staticmethod
    def init_stock(producto_id: int, localidad_id: int, lugar_id: int, cantidad: int = 0) -> bool:
        """
        Inicializar stock de un producto en un lugar
        
        Args:
            producto_id: ID del producto
            localidad_id: ID de la localidad
            lugar_id: ID del lugar
            cantidad: Cantidad inicial (default 0)
        """
        try:
            with ConectDB.get_cursor() as cursor:
                query = """
                    INSERT INTO productos_localidad 
                    (id_producto, id_localidad, id_lugar, cantidad)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE cantidad = %s
                """
                cursor.execute(query, (producto_id, localidad_id, lugar_id, cantidad, cantidad))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error init stock: {e}")
            raise
    
    @staticmethod
    def get_stock(producto_id: int, lugar_id: int) -> int:
        """
        Obtener cantidad de stock de un producto en un lugar específico
        """
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
            print(f"Error getting stock: {e}")
            raise
    
    @staticmethod
    def sumar_stock(producto_id: int, lugar_id: int, cantidad: int) -> bool:
        """
        Sumar stock a un lugar (para entradas)
        
        Args:
            producto_id: ID del producto
            lugar_id: ID del lugar
            cantidad: Cantidad a sumar
        """
        try:
            with ConectDB.get_cursor() as cursor:
                # Verificar si existe el registro
                query_check = """
                    SELECT id_producto, id_localidad 
                    FROM productos_localidad 
                    WHERE id_producto = %s AND id_lugar = %s
                """
                cursor.execute(query_check, (producto_id, lugar_id))
                existe = cursor.fetchone()
                
                if existe:
                    # Actualizar stock existente
                    query = """
                        UPDATE productos_localidad 
                        SET cantidad = cantidad + %s
                        WHERE id_producto = %s AND id_lugar = %s
                    """
                    cursor.execute(query, (cantidad, producto_id, lugar_id))
                else:
                    # Crear registro nuevo (obtener localidad del lugar)
                    query_loc = "SELECT id_localidad FROM lugares WHERE id_lugar = %s"
                    cursor.execute(query_loc, (lugar_id,))
                    lugar = cursor.fetchone()
                    
                    if not lugar:
                        raise Exception(f"Lugar {lugar_id} no encontrado")
                    
                    query = """
                        INSERT INTO productos_localidad 
                        (id_producto, id_localidad, id_lugar, cantidad)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(query, (producto_id, lugar['id_localidad'], lugar_id, cantidad))
                
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error sumando stock: {e}")
            raise
    
    @staticmethod
    def restar_stock(producto_id: int, lugar_id: int, cantidad: int) -> bool:
        """
        Restar stock de un lugar (para salidas)
        VALIDA que haya stock suficiente
        
        Args:
            producto_id: ID del producto
            lugar_id: ID del lugar
            cantidad: Cantidad a restar
        
        Raises:
            Exception: Si no hay stock suficiente
        """
        try:
            with ConectDB.get_cursor() as cursor:
                # Verificar stock actual
                stock_actual = ProductoLocalidadDAO.get_stock(producto_id, lugar_id)
                
                if stock_actual < cantidad:
                    raise Exception(f"Stock insuficiente. Disponible: {stock_actual}, Requerido: {cantidad}")
                
                # Restar stock
                query = """
                    UPDATE productos_localidad 
                    SET cantidad = cantidad - %s
                    WHERE id_producto = %s AND id_lugar = %s
                """
                cursor.execute(query, (cantidad, producto_id, lugar_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error restando stock: {e}")
            raise
    
    @staticmethod
    def transferir_stock(producto_id: int, lugar_origen: int, lugar_destino: int, cantidad: int) -> bool:
        """
        Transferir stock entre lugares
        
        Args:
            producto_id: ID del producto
            lugar_origen: ID del lugar origen
            lugar_destino: ID del lugar destino
            cantidad: Cantidad a transferir
        """
        try:
            with ConectDB.get_cursor() as cursor:
                # Validar stock en origen
                stock_origen = ProductoLocalidadDAO.get_stock(producto_id, lugar_origen)
                
                if stock_origen < cantidad:
                    raise Exception(f"Stock insuficiente en origen. Disponible: {stock_origen}")
                
                # Restar de origen
                ProductoLocalidadDAO.restar_stock(producto_id, lugar_origen, cantidad)
                
                # Sumar a destino
                ProductoLocalidadDAO.sumar_stock(producto_id, lugar_destino, cantidad)
                
                return True
        except Exception as e:
            print(f"Error transfiriendo stock: {e}")
            raise
    
    @staticmethod
    def ajustar_stock(producto_id: int, lugar_id: int, cantidad_nueva: int, motivo: str = '') -> bool:
        """
        Ajustar stock a una cantidad específica (inventario físico)
        
        Args:
            producto_id: ID del producto
            lugar_id: ID del lugar
            cantidad_nueva: Nueva cantidad
            motivo: Motivo del ajuste
        """
        try:
            with ConectDB.get_cursor() as cursor:
                query = """
                    UPDATE productos_localidad 
                    SET cantidad = %s
                    WHERE id_producto = %s AND id_lugar = %s
                """
                cursor.execute(query, (cantidad_nueva, producto_id, lugar_id))
                
                if cursor.rowcount == 0:
                    # No existe, crear
                    query_loc = "SELECT id_localidad FROM lugares WHERE id_lugar = %s"
                    cursor.execute(query_loc, (lugar_id,))
                    lugar = cursor.fetchone()
                    
                    query_insert = """
                        INSERT INTO productos_localidad 
                        (id_producto, id_localidad, id_lugar, cantidad)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(query_insert, (producto_id, lugar['id_localidad'], lugar_id, cantidad_nueva))
                
                return True
        except Exception as e:
            print(f"Error ajustando stock: {e}")
            raise
    
    @staticmethod
    def get_stock_por_producto(producto_id: int) -> list:
        """Obtener stock de un producto en todos los lugares"""
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
            print(f"Error getting stock por producto: {e}")
            raise
    
    @staticmethod
    def get_stock_por_localidad(localidad_id: int) -> list:
        """Obtener stock de todos los productos en una localidad"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = """
                    SELECT pl.*, 
                           p.nombre as producto_nombre,
                           p.codigo as producto_codigo,
                           lug.nombre as lugar_nombre
                    FROM productos_localidad pl
                    JOIN productos p ON pl.id_producto = p.id_producto
                    JOIN lugares lug ON pl.id_lugar = lug.id_lugar
                    WHERE pl.id_localidad = %s AND pl.cantidad > 0
                    ORDER BY p.nombre, lug.nombre
                """
                cursor.execute(query, (localidad_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting stock por localidad: {e}")
            raise
    
    @staticmethod
    def get_total_por_producto(producto_id: int) -> int:
        """Obtener stock total de un producto (suma de todos los lugares)"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = """
                    SELECT COALESCE(SUM(cantidad), 0) as total
                    FROM productos_localidad
                    WHERE id_producto = %s
                """
                cursor.execute(query, (producto_id,))
                result = cursor.fetchone()
                return result['total']
        except Exception as e:
            print(f"Error getting total stock: {e}")
            raise