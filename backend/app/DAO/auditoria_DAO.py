"""
DAO de Auditoría
Registra TODAS las acciones realizadas en el sistema
"""

from app.db.conexion_DB import ConectDB
import json


class AuditoriaDAO:
    """Data Access Object para la tabla auditoria"""
    
    @staticmethod
    def create(data: dict) -> int:
        """
        Registrar una acción en auditoría
        
        Args:
            data (dict): {
                'entidad': str (Usuario, Producto, Envio, etc.),
                'id_entidad': int,
                'accion': str (create, update, delete, envio, recepcion, etc.),
                'descripcion': str,
                'datos_anteriores': dict (opcional),
                'datos_nuevos': dict (opcional),
                'id_usuario': int,
                'ip_address': str (opcional),
                'user_agent': str (opcional)
            }
        """
        try:
            connection = ConectDB.get_connection()
            with connection.cursor() as cursor:
                # Convertir diccionarios a JSON
                datos_anteriores = json.dumps(data.get('datos_anteriores')) if data.get('datos_anteriores') else None
                datos_nuevos = json.dumps(data.get('datos_nuevos')) if data.get('datos_nuevos') else None
                
                query = """
                    INSERT INTO auditoria 
                    (entidad, id_entidad, accion, descripcion, 
                     datos_anteriores, datos_nuevos, id_usuario, 
                     ip_address, user_agent)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    data['entidad'],
                    data['id_entidad'],
                    data['accion'],
                    data.get('descripcion', ''),
                    datos_anteriores,
                    datos_nuevos,
                    data['id_usuario'],
                    data.get('ip_address'),
                    data.get('user_agent')
                ))
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating auditoria: {e}")
            raise
    
    @staticmethod
    def get_all(page=1, limit=50, entidad=None, accion=None, usuario_id=None, 
                fecha_desde=None, fecha_hasta=None):
        """Obtener todos los registros de auditoría con filtros"""
        try:
            with ConectDB.get_cursor() as cursor:
                # Contar total
                count_query = "SELECT COUNT(*) as total FROM auditoria WHERE 1=1"
                params = []
                
                if entidad:
                    count_query += " AND entidad = %s"
                    params.append(entidad)
                
                if accion:
                    count_query += " AND accion = %s"
                    params.append(accion)
                
                if usuario_id:
                    count_query += " AND id_usuario = %s"
                    params.append(usuario_id)
                
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
                    SELECT a.*,
                           u.nombre as usuario_nombre,
                           u.apellido as usuario_apellido,
                           u.username
                    FROM auditoria a
                    JOIN usuarios u ON a.id_usuario = u.id_usuario
                    WHERE 1=1
                """
                
                if entidad:
                    query += " AND a.entidad = %s"
                
                if accion:
                    query += " AND a.accion = %s"
                
                if usuario_id:
                    query += " AND a.id_usuario = %s"
                
                if fecha_desde:
                    query += " AND a.fecha_hora >= %s"
                
                if fecha_hasta:
                    query += " AND a.fecha_hora <= %s"
                
                query += " ORDER BY a.fecha_hora DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                auditorias = cursor.fetchall()
                
                # Parsear JSON
                for aud in auditorias:
                    if aud.get('datos_anteriores'):
                        aud['datos_anteriores'] = json.loads(aud['datos_anteriores'])
                    if aud.get('datos_nuevos'):
                        aud['datos_nuevos'] = json.loads(aud['datos_nuevos'])
                
                return {
                    'auditorias': auditorias,
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total': total,
                        'total_pages': (total + limit - 1) // limit
                    }
                }
        except Exception as e:
            print(f"Error getting auditorias: {e}")
            raise
    
    @staticmethod
    def get_by_usuario(usuario_id: int, page=1, limit=50) -> dict:
        """Obtener auditoría de un usuario específico"""
        return AuditoriaDAO.get_all(page=page, limit=limit, usuario_id=usuario_id)
    
    @staticmethod
    def get_by_entidad(entidad: str, id_entidad: int) -> list:
        """Obtener historial de auditoría de una entidad específica"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = """
                    SELECT a.*,
                           u.nombre as usuario_nombre,
                           u.apellido as usuario_apellido
                    FROM auditoria a
                    JOIN usuarios u ON a.id_usuario = u.id_usuario
                    WHERE a.entidad = %s AND a.id_entidad = %s
                    ORDER BY a.fecha_hora DESC
                """
                cursor.execute(query, (entidad, id_entidad))
                auditorias = cursor.fetchall()
                
                # Parsear JSON
                for aud in auditorias:
                    if aud.get('datos_anteriores'):
                        aud['datos_anteriores'] = json.loads(aud['datos_anteriores'])
                    if aud.get('datos_nuevos'):
                        aud['datos_nuevos'] = json.loads(aud['datos_nuevos'])
                
                return auditorias
        except Exception as e:
            print(f"Error getting auditoria by entidad: {e}")
            raise
    
    @staticmethod
    def get_actividad_reciente(limit: int = 20) -> list:
        """Obtener actividad reciente del sistema"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = """
                    SELECT a.*,
                           u.nombre as usuario_nombre,
                           u.apellido as usuario_apellido
                    FROM auditoria a
                    JOIN usuarios u ON a.id_usuario = u.id_usuario
                    ORDER BY a.fecha_hora DESC
                    LIMIT %s
                """
                cursor.execute(query, (limit,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting actividad reciente: {e}")
            raise
    
    @staticmethod
    def count_por_accion(fecha_desde=None, fecha_hasta=None) -> dict:
        """Contar acciones por tipo"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = "SELECT accion, COUNT(*) as count FROM auditoria WHERE 1=1"
                params = []
                
                if fecha_desde:
                    query += " AND fecha_hora >= %s"
                    params.append(fecha_desde)
                
                if fecha_hasta:
                    query += " AND fecha_hora <= %s"
                    params.append(fecha_hasta)
                
                query += " GROUP BY accion"
                cursor.execute(query, params)
                
                results = cursor.fetchall()
                return {row['accion']: row['count'] for row in results}
        except Exception as e:
            print(f"Error counting por accion: {e}")
            raise
    
    @staticmethod
    def count_por_usuario(fecha_desde=None, fecha_hasta=None) -> list:
        """Contar acciones por usuario"""
        try:
            with ConectDB.get_cursor() as cursor:
                query = """
                    SELECT u.id_usuario, u.nombre, u.apellido, COUNT(*) as count
                    FROM auditoria a
                    JOIN usuarios u ON a.id_usuario = u.id_usuario
                    WHERE 1=1
                """
                params = []
                
                if fecha_desde:
                    query += " AND a.fecha_hora >= %s"
                    params.append(fecha_desde)
                
                if fecha_hasta:
                    query += " AND a.fecha_hora <= %s"
                    params.append(fecha_hasta)
                
                query += " GROUP BY u.id_usuario ORDER BY count DESC"
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error counting por usuario: {e}")
            raise