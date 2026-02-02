"""
DAO de Envíos
Maneja envíos de productos entre localidades
"""

from app.db.conexion_DB import ConectDB


class EnvioDAO:
    """Data Access Object para la tabla envios"""
    
    @staticmethod
    def create(data: dict) -> int:
        """
        Crear un nuevo envío
        
        Args:
            data (dict): {
                'id_producto': int,
                'cantidad': int,
                'id_usuario_envia': int,
                'localidad_origen': int,
                'localidad_destino': int,
                'lugar_origen': int,
                'lugar_destino': int (opcional),
                'motivo': str,
                'observaciones_envio': str
            }
        """
        try:
            with ConectDB.get_cursor() as cursor:
                query = """
                    INSERT INTO envios 
                    (id_producto, cantidad, id_usuario_envia, 
                     localidad_origen, localidad_destino, 
                     lugar_origen, lugar_destino, 
                     estado, motivo, observaciones_envio)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'enviado', %s, %s)
                """
                cursor.execute(query, (
                    data['id_producto'],
                    data['cantidad'],
                    data['id_usuario_envia'],
                    data['localidad_origen'],
                    data['localidad_destino'],
                    data['lugar_origen'],
                    data.get('lugar_destino'),
                    data.get('motivo', ''),
                    data.get('observaciones_envio', '')
                ))
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating envio: {e}")
            raise
    
    @staticmethod
    def get_all(page=1, limit=20, estado=None, localidad_origen=None, 
                localidad_destino=None, producto_id=None):
        """Obtener todos los envíos con filtros"""
        try:
            with ConectDB.get_cursor() as cursor:
                # Contar total
                count_query = "SELECT COUNT(*) as total FROM envios WHERE 1=1"
                params = []
                
                if estado:
                    count_query += " AND estado = %s"
                    params.append(estado)
                
                if localidad_origen:
                    count_query += " AND localidad_origen = %s"
                    params.append(localidad_origen)
                
                if localidad_destino:
                    count_query += " AND localidad_destino = %s"
                    params.append(localidad_destino)
                
                if producto_id:
                    count_query += " AND id_producto = %s"
                    params.append(producto_id)
                
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']
                
                # Obtener registros
                offset = (page - 1) * limit
                query = """
                    SELECT e.*,
                           p.nombre as producto_nombre,
                           p.codigo as producto_codigo,
                           ue.nombre as usuario_envia_nombre,
                           ue.apellido as usuario_envia_apellido,
                           ur.nombre as usuario_recibe_nombre,
                           ur.apellido as usuario_recibe_apellido,
                           lo_origen.nombre as localidad_origen_nombre,
                           lo_destino.nombre as localidad_destino_nombre,
                           lug_origen.nombre as lugar_origen_nombre,
                           lug_destino.nombre as lugar_destino_nombre
                    FROM envios e
                    JOIN productos p ON e.id_producto = p.id_producto
                    JOIN usuarios ue ON e.id_usuario_envia = ue.id_usuario
                    LEFT JOIN usuarios ur ON e.id_usuario_recibe = ur.id_usuario
                    JOIN localidades lo_origen ON e.localidad_origen = lo_origen.id_localidad
                    JOIN localidades lo_destino ON e.localidad_destino = lo_destino.id_localidad
                    JOIN lugares lug_origen ON e.lugar_origen = lug_origen.id_lugar
                    LEFT JOIN lugares lug_destino ON e.lugar_destino = lug_destino.id_lugar
                    WHERE 1=1
                """
                
                if estado:
                    query += " AND e.estado = %s"
                
                if localidad_origen:
                    query += " AND e.localidad_origen = %s"
                
                if localidad_destino:
                    query += " AND e.localidad_destino = %s"
                
                if producto_id:
                    query += " AND e.id_producto = %s"
                
                query += " ORDER BY e.fecha_envio DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                envios = cursor.fetchall()
                
                return {
                    'envios': envios,
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total': total,
                        'total_pages': (total + limit - 1) // limit
                    }
                }
        except Exception as e:
            print(f"Error getting envios: {e}")
            raise
    
    @staticmethod
    def get_by_id(envio_id: int) -> dict:
        """Obtener un envío por ID"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = """
                    SELECT e.*,
                           p.nombre as producto_nombre,
                           p.codigo as producto_codigo,
                           ue.nombre as usuario_envia_nombre,
                           ue.apellido as usuario_envia_apellido,
                           ur.nombre as usuario_recibe_nombre,
                           ur.apellido as usuario_recibe_apellido,
                           lo_origen.nombre as localidad_origen_nombre,
                           lo_destino.nombre as localidad_destino_nombre,
                           lug_origen.nombre as lugar_origen_nombre,
                           lug_destino.nombre as lugar_destino_nombre
                    FROM envios e
                    JOIN productos p ON e.id_producto = p.id_producto
                    JOIN usuarios ue ON e.id_usuario_envia = ue.id_usuario
                    LEFT JOIN usuarios ur ON e.id_usuario_recibe = ur.id_usuario
                    JOIN localidades lo_origen ON e.localidad_origen = lo_origen.id_localidad
                    JOIN localidades lo_destino ON e.localidad_destino = lo_destino.id_localidad
                    JOIN lugares lug_origen ON e.lugar_origen = lug_origen.id_lugar
                    LEFT JOIN lugares lug_destino ON e.lugar_destino = lug_destino.id_lugar
                    WHERE e.id_envio = %s
                """
                cursor.execute(query, (envio_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting envio by id: {e}")
            raise
    
    @staticmethod
    def get_pendientes_recepcion(localidad_destino: int) -> list:
        """Obtener envíos pendientes de recibir en una localidad"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = """
                    SELECT e.*,
                           p.nombre as producto_nombre,
                           lo.nombre as localidad_origen_nombre
                    FROM envios e
                    JOIN productos p ON e.id_producto = p.id_producto
                    JOIN localidades lo ON e.localidad_origen = lo.id_localidad
                    WHERE e.localidad_destino = %s 
                    AND e.estado IN ('enviado', 'en_transito')
                    ORDER BY e.fecha_envio DESC
                """
                cursor.execute(query, (localidad_destino,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting pendientes recepcion: {e}")
            raise
    
    @staticmethod
    def marcar_recibido(envio_id: int, usuario_recibe_id: int, lugar_destino_id: int, observaciones: str = '') -> bool:
        """
        Marcar un envío como recibido
        
        Args:
            envio_id: ID del envío
            usuario_recibe_id: ID del usuario que recibe
            lugar_destino_id: ID del lugar donde se recibe
            observaciones: Observaciones de recepción
        """
        try:
            with ConectDB.get_cursor() as cursor:
                query = """
                    UPDATE envios 
                    SET estado = 'recibido',
                        id_usuario_recibe = %s,
                        lugar_destino = %s,
                        fecha_recepcion = NOW(),
                        observaciones_recepcion = %s
                    WHERE id_envio = %s AND estado IN ('enviado', 'en_transito')
                """
                cursor.execute(query, (usuario_recibe_id, lugar_destino_id, observaciones, envio_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error marcando recibido: {e}")
            raise
    
    @staticmethod
    def cancelar(envio_id: int, observaciones: str = '') -> bool:
        """Cancelar un envío"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = """
                    UPDATE envios 
                    SET estado = 'cancelado',
                        fecha_cancelacion = NOW(),
                        observaciones_cancelacion = %s
                    WHERE id_envio = %s AND estado != 'recibido'
                """
                cursor.execute(query, (observaciones, envio_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error cancelando envio: {e}")
            raise
    
    @staticmethod
    def update_estado(envio_id: int, nuevo_estado: str) -> bool:
        """Actualizar estado del envío"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = "UPDATE envios SET estado = %s WHERE id_envio = %s"
                cursor.execute(query, (nuevo_estado, envio_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating estado: {e}")
            raise
    
    @staticmethod
    def get_por_usuario_envia(usuario_id: int) -> list:
        """Obtener envíos realizados por un usuario"""
        result = EnvioDAO.get_all(page=1, limit=100)
        return [e for e in result['envios'] if e['id_usuario_envia'] == usuario_id]
    
    @staticmethod
    def get_por_usuario_recibe(usuario_id: int) -> list:
        """Obtener envíos recibidos por un usuario"""
        result = EnvioDAO.get_all(page=1, limit=100)
        return [e for e in result['envios'] if e.get('id_usuario_recibe') == usuario_id]