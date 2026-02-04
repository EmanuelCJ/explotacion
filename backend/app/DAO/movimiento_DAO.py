"""
DAO de Movimientos
Registra entradas, salidas, transferencias y ajustes de stock
"""

from app.db.conexion_DB import ConectDB


class MovimientoDAO:
    """Data Access Object para la tabla movimientos"""
    
    @staticmethod
    def create(data: dict) -> int:
        """
        Crear un nuevo movimiento
        
        Args:
            data (dict): {
                'tipo': str (entrada, salida, transferencia, ajuste),
                'cantidad': int,
                'id_producto': int,
                'id_usuario': int,
                'id_localidad': int,
                'lugar_origen': int (opcional),
                'lugar_destino': int (opcional),
                'motivo': str,
                'observaciones': str
            }
        """
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO movimientos 
                    (tipo, cantidad, id_producto, id_usuario, id_localidad,
                     lugar_origen, lugar_destino, motivo, observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    data['tipo'],
                    data['cantidad'],
                    data['id_producto'],
                    data['id_usuario'],
                    data['id_localidad'],
                    data.get('lugar_origen'),
                    data.get('lugar_destino'),
                    data.get('motivo', ''),
                    data.get('observaciones', '')
                ))
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating movimiento: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_all(page=1, limit=20, tipo=None, producto_id=None, usuario_id=None, 
                localidad_id=None, fecha_desde=None, fecha_hasta=None):
        """Obtener todos los movimientos con filtros y paginación"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                # Contar total
                count_query = "SELECT COUNT(*) as total FROM movimientos WHERE 1=1"
                params = []
                
                if tipo:
                    count_query += " AND tipo = %s"
                    params.append(tipo)
                
                if producto_id:
                    count_query += " AND id_producto = %s"
                    params.append(producto_id)
                
                if usuario_id:
                    count_query += " AND id_usuario = %s"
                    params.append(usuario_id)
                
                if localidad_id:
                    count_query += " AND id_localidad = %s"
                    params.append(localidad_id)
                
                if fecha_desde:
                    count_query += " AND fecha_hora >= %s"
                    params.append(fecha_desde)
                
                if fecha_hasta:
                    count_query += " AND fecha_hora <= %s"
                    params.append(fecha_hasta)
                
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']
                
                # Obtener registros
                offset = (page - 1) * limit
                query = """
                    SELECT m.*,
                           p.nombre as producto_nombre,
                           p.codigo as producto_codigo,
                           u.nombre as usuario_nombre,
                           u.apellido as usuario_apellido,
                           loc.nombre as localidad_nombre,
                           lo.nombre as lugar_origen_nombre,
                           ld.nombre as lugar_destino_nombre
                    FROM movimientos m
                    JOIN productos p ON m.id_producto = p.id_producto
                    JOIN usuarios u ON m.id_usuario = u.id_usuario
                    JOIN localidades loc ON m.id_localidad = loc.id_localidad
                    LEFT JOIN lugares lo ON m.lugar_origen = lo.id_lugar
                    LEFT JOIN lugares ld ON m.lugar_destino = ld.id_lugar
                    WHERE 1=1
                """
                
                if tipo:
                    query += " AND m.tipo = %s"
                
                if producto_id:
                    query += " AND m.id_producto = %s"
                
                if usuario_id:
                    query += " AND m.id_usuario = %s"
                
                if localidad_id:
                    query += " AND m.id_localidad = %s"
                
                if fecha_desde:
                    query += " AND m.fecha_hora >= %s"
                
                if fecha_hasta:
                    query += " AND m.fecha_hora <= %s"
                
                query += " ORDER BY m.fecha_hora DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                movimientos = cursor.fetchall()
                
                return {
                    'movimientos': movimientos,
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total': total,
                        'total_pages': (total + limit - 1) // limit
                    }
                }
        except Exception as e:
            print(f"Error getting movimientos: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(movimiento_id: int) -> dict:
        """Obtener un movimiento por ID"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT m.*,
                           p.nombre as producto_nombre,
                           p.codigo as producto_codigo,
                           u.nombre as usuario_nombre,
                           u.apellido as usuario_apellido,
                           loc.nombre as localidad_nombre,
                           lo.nombre as lugar_origen_nombre,
                           ld.nombre as lugar_destino_nombre
                    FROM movimientos m
                    JOIN productos p ON m.id_producto = p.id_producto
                    JOIN usuarios u ON m.id_usuario = u.id_usuario
                    JOIN localidades loc ON m.id_localidad = loc.id_localidad
                    LEFT JOIN lugares lo ON m.lugar_origen = lo.id_lugar
                    LEFT JOIN lugares ld ON m.lugar_destino = ld.id_lugar
                    WHERE m.id_movimiento = %s
                """
                cursor.execute(query, (movimiento_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting movimiento by id: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def get_by_producto(producto_id: int, page=1, limit=20) -> dict:
        """Obtener movimientos de un producto específico"""
        return MovimientoDAO.get_all(page=page, limit=limit, producto_id=producto_id)
    
    @staticmethod
    def get_by_usuario(usuario_id: int, page=1, limit=20) -> dict:
        """Obtener movimientos realizados por un usuario"""
        return MovimientoDAO.get_all(page=page, limit=limit, usuario_id=usuario_id)
    
    @staticmethod
    def get_by_localidad(localidad_id: int, page=1, limit=20) -> dict:
        """Obtener movimientos de una localidad"""
        return MovimientoDAO.get_all(page=page, limit=limit, localidad_id=localidad_id)
    
    @staticmethod
    def get_ultimos(limit: int = 10) -> list:
        """Obtener los últimos N movimientos"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT m.*,
                           p.nombre as producto_nombre,
                           u.nombre as usuario_nombre,
                           u.apellido as usuario_apellido,
                           loc.nombre as localidad_nombre
                    FROM movimientos m
                    JOIN productos p ON m.id_producto = p.id_producto
                    JOIN usuarios u ON m.id_usuario = u.id_usuario
                    JOIN localidades loc ON m.id_localidad = loc.id_localidad
                    ORDER BY m.fecha_hora DESC
                    LIMIT %s
                """
                cursor.execute(query, (limit,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting ultimos movimientos: {e}")
            raise
        finally:
            connection.close()
    
    @staticmethod
    def count_por_tipo(fecha_desde=None, fecha_hasta=None) -> dict:
        """Contar movimientos por tipo en un rango de fechas"""
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT tipo, COUNT(*) as count, SUM(cantidad) as total_cantidad
                    FROM movimientos
                    WHERE 1=1
                """
                params = []
                
                if fecha_desde:
                    query += " AND fecha_hora >= %s"
                    params.append(fecha_desde)
                
                if fecha_hasta:
                    query += " AND fecha_hora <= %s"
                    params.append(fecha_hasta)
                
                query += " GROUP BY tipo"
                cursor.execute(query, params)
                
                results = cursor.fetchall()
                return {row['tipo']: {'count': row['count'], 'total': row['total_cantidad']} for row in results}
        except Exception as e:
            print(f"Error counting por tipo: {e}")
            raise
        finally:
            connection.close()