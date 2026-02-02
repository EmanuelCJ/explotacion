"""
Servicio de Envíos
Maneja envíos de productos entre localidades
Al enviar: resta stock del origen
Al recibir: suma stock al destino
"""

from app.DAO.envio_DAO import EnvioDAO
from app.DAO.producto_DAO import ProductoDAO
from app.DAO.producto_localidad_DAO import ProductoLocalidadDAO
from app.DAO.lugar_DAO import LugarDAO
from app.DAO.localidad_DAO import LocalidadDAO
from app.DAO.auditoria_DAO import AuditoriaDAO


class EnvioService:
    """Servicio de gestión de envíos entre localidades"""
    
    @staticmethod
    def crear_envio(data: dict, usuario_envia_id: int) -> int:
        """
        Crear un nuevo envío
        RESTA el stock del lugar de origen
        
        Args:
            data (dict): {
                'id_producto': int,
                'cantidad': int,
                'localidad_destino': int,
                'lugar_origen': int,
                'lugar_destino': int (opcional),
                'motivo': str,
                'observaciones_envio': str (opcional)
            }
            usuario_envia_id: ID del usuario que envía
        
        Returns:
            int: ID del envío creado
        """
        # Validaciones
        EnvioService._validate_envio_data(data)
        
        # Verificar producto
        producto = ProductoDAO.get_by_id(data['id_producto'])
        if not producto:
            raise Exception("Producto no encontrado")
        
        # Verificar lugares
        lugar_origen = LugarDAO.get_by_id(data['lugar_origen'])
        if not lugar_origen:
            raise Exception("Lugar de origen no encontrado")
        
        localidad_origen = lugar_origen['id_localidad']
        
        # Verificar localidad destino
        localidad_destino = LocalidadDAO.get_by_id(data['localidad_destino'])
        if not localidad_destino:
            raise Exception("Localidad de destino no encontrada")
        
        # No permitir envío a la misma localidad
        if localidad_origen == data['localidad_destino']:
            raise Exception("No se puede enviar a la misma localidad. Use transferencias.")
        
        # VALIDAR STOCK DISPONIBLE
        stock_disponible = ProductoLocalidadDAO.get_stock(
            data['id_producto'],
            data['lugar_origen']
        )
        
        if stock_disponible < data['cantidad']:
            raise Exception(
                f"Stock insuficiente. Disponible: {stock_disponible}, "
                f"Solicitado: {data['cantidad']}"
            )
        
        # Preparar datos del envío
        envio_data = {
            'id_producto': data['id_producto'],
            'cantidad': data['cantidad'],
            'id_usuario_envia': usuario_envia_id,
            'localidad_origen': localidad_origen,
            'localidad_destino': data['localidad_destino'],
            'lugar_origen': data['lugar_origen'],
            'lugar_destino': data.get('lugar_destino'),
            'motivo': data.get('motivo', ''),
            'observaciones_envio': data.get('observaciones_envio', '')
        }
        
        # Crear envío
        envio_id = EnvioDAO.create(envio_data)
        
        # RESTAR STOCK DEL ORIGEN
        ProductoLocalidadDAO.restar_stock(
            data['id_producto'],
            data['lugar_origen'],
            data['cantidad']
        )
        
        # Registrar en auditoría
        AuditoriaDAO.create({
            'entidad': 'Envio',
            'id_entidad': envio_id,
            'accion': 'envio',
            'descripcion': (
                f"Envío de {data['cantidad']} unidades de {producto['nombre']} "
                f"desde {lugar_origen['nombre']} ({lugar_origen['localidad_nombre']}) "
                f"hacia {localidad_destino['nombre']}"
            ),
            'datos_nuevos': envio_data,
            'id_usuario': usuario_envia_id
        })
        
        return envio_id
    
    @staticmethod
    def recibir_envio(envio_id: int, usuario_recibe_id: int, lugar_destino_id: int, 
                      observaciones: str = '') -> bool:
        """
        Marcar un envío como recibido
        SUMA el stock al lugar de destino
        
        Args:
            envio_id: ID del envío
            usuario_recibe_id: ID del usuario que recibe
            lugar_destino_id: ID del lugar donde se recibe
            observaciones: Observaciones de recepción
        
        Returns:
            bool: True si se recibió correctamente
        """
        # Obtener envío
        envio = EnvioDAO.get_by_id(envio_id)
        if not envio:
            raise Exception("Envío no encontrado")
        
        # Validar estado
        if envio['estado'] == 'recibido':
            raise Exception("El envío ya fue recibido")
        
        if envio['estado'] == 'cancelado':
            raise Exception("El envío está cancelado")
        
        # Verificar lugar destino
        lugar_destino = LugarDAO.get_by_id(lugar_destino_id)
        if not lugar_destino:
            raise Exception("Lugar de destino no encontrado")
        
        # Verificar que el lugar pertenezca a la localidad destino
        if lugar_destino['id_localidad'] != envio['localidad_destino']:
            raise Exception("El lugar no pertenece a la localidad de destino")
        
        # Marcar como recibido
        success = EnvioDAO.marcar_recibido(
            envio_id,
            usuario_recibe_id,
            lugar_destino_id,
            observaciones
        )
        
        if success:
            # SUMAR STOCK AL DESTINO
            ProductoLocalidadDAO.sumar_stock(
                envio['id_producto'],
                lugar_destino_id,
                envio['cantidad']
            )
            
            # Registrar en auditoría
            AuditoriaDAO.create({
                'entidad': 'Envio',
                'id_entidad': envio_id,
                'accion': 'recepcion',
                'descripcion': (
                    f"Recepción de {envio['cantidad']} unidades de "
                    f"{envio['producto_nombre']} en {lugar_destino['nombre']}"
                ),
                'datos_nuevos': {
                    'usuario_recibe': usuario_recibe_id,
                    'lugar_destino': lugar_destino_id,
                    'observaciones': observaciones
                },
                'id_usuario': usuario_recibe_id
            })
        
        return success
    
    @staticmethod
    def cancelar_envio(envio_id: int, usuario_id: int, observaciones: str = '') -> bool:
        """
        Cancelar un envío
        DEVUELVE el stock al origen si aún no fue recibido
        
        Args:
            envio_id: ID del envío
            usuario_id: ID del usuario que cancela
            observaciones: Motivo de cancelación
        
        Returns:
            bool: True si se canceló correctamente
        """
        # Obtener envío
        envio = EnvioDAO.get_by_id(envio_id)
        if not envio:
            raise Exception("Envío no encontrado")
        
        # Validar estado
        if envio['estado'] == 'cancelado':
            raise Exception("El envío ya está cancelado")
        
        if envio['estado'] == 'recibido':
            raise Exception("No se puede cancelar un envío ya recibido")
        
        # Cancelar envío
        success = EnvioDAO.cancelar(envio_id, observaciones)
        
        if success:
            # DEVOLVER STOCK AL ORIGEN
            ProductoLocalidadDAO.sumar_stock(
                envio['id_producto'],
                envio['lugar_origen'],
                envio['cantidad']
            )
            
            # Registrar en auditoría
            AuditoriaDAO.create({
                'entidad': 'Envio',
                'id_entidad': envio_id,
                'accion': 'cancelacion',
                'descripcion': (
                    f"Cancelación de envío de {envio['cantidad']} unidades de "
                    f"{envio['producto_nombre']}. Motivo: {observaciones}"
                ),
                'datos_nuevos': {'observaciones': observaciones},
                'id_usuario': usuario_id
            })
        
        return success
    
    @staticmethod
    def get_all(page=1, limit=20, estado=None, localidad_origen=None, 
                localidad_destino=None, producto_id=None):
        """Obtener todos los envíos con filtros"""
        return EnvioDAO.get_all(
            page=page,
            limit=limit,
            estado=estado,
            localidad_origen=localidad_origen,
            localidad_destino=localidad_destino,
            producto_id=producto_id
        )
    
    @staticmethod
    def get_by_id(envio_id: int) -> dict:
        """Obtener un envío por ID"""
        return EnvioDAO.get_by_id(envio_id)
    
    @staticmethod
    def get_pendientes_recepcion(localidad_id: int) -> list:
        """Obtener envíos pendientes de recibir en una localidad"""
        return EnvioDAO.get_pendientes_recepcion(localidad_id)
    
    @staticmethod
    def get_mis_envios(usuario_id: int) -> list:
        """Obtener envíos realizados por un usuario"""
        return EnvioDAO.get_por_usuario_envia(usuario_id)
    
    @staticmethod
    def get_mis_recepciones(usuario_id: int) -> list:
        """Obtener envíos recibidos por un usuario"""
        return EnvioDAO.get_por_usuario_recibe(usuario_id)
    
    @staticmethod
    def _validate_envio_data(data: dict):
        """Validar datos de envío"""
        required = ['id_producto', 'cantidad', 'localidad_destino', 'lugar_origen']
        
        for field in required:
            if field not in data or not data[field]:
                raise Exception(f"Campo requerido: {field}")
        
        if data['cantidad'] <= 0:
            raise Exception("La cantidad debe ser mayor a 0")