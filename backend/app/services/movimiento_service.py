"""
Servicio de Movimientos
CRÍTICO: Maneja entradas, salidas, transferencias y ajustes de stock
Actualiza automáticamente el stock en productos_localidad
"""

from app.DAO.movimiento_DAO import MovimientoDAO
from app.DAO.producto_DAO import ProductoDAO
from app.DAO.producto_localidad_DAO import ProductoLocalidadDAO
from app.DAO.lugar_DAO import LugarDAO
from app.DAO.auditoria_DAO import AuditoriaDAO


class MovimientoService:
    """Servicio de gestión de movimientos de inventario"""
    
    @staticmethod
    def crear_entrada(data: dict, usuario_id: int, localidad_id: int) -> int:
        """
        Registrar entrada de stock
        
        Args:
            data (dict): {
                'id_producto': int,
                'cantidad': int,
                'lugar_destino': int,
                'motivo': str,
                'observaciones': str (opcional)
            }
            usuario_id: ID del usuario que registra
            localidad_id: ID de la localidad
        
        Returns:
            int: ID del movimiento creado
        """
        # Validaciones
        MovimientoService._validate_movimiento_data(data, 'entrada')
        
        # Verificar que existe el producto
        producto = ProductoDAO.get_by_id(data['id_producto'])
        if not producto:
            raise Exception("Producto no encontrado")
        
        # Verificar que existe el lugar
        lugar = LugarDAO.get_by_id(data['lugar_destino'])
        if not lugar:
            raise Exception("Lugar de destino no encontrado")
        
        # Crear movimiento
        movimiento_data = {
            'tipo': 'entrada',
            'cantidad': data['cantidad'],
            'id_producto': data['id_producto'],
            'id_usuario': usuario_id,
            'id_localidad': localidad_id,
            'lugar_destino': data['lugar_destino'],
            'motivo': data.get('motivo', ''),
            'observaciones': data.get('observaciones', '')
        }
        
        movimiento_id = MovimientoDAO.create(movimiento_data)
        
        # ACTUALIZAR STOCK (sumar)
        ProductoLocalidadDAO.sumar_stock(
            data['id_producto'],
            data['lugar_destino'],
            data['cantidad']
        )
        
        # Registrar en auditoría
        AuditoriaDAO.create({
            'entidad': 'Movimiento',
            'id_entidad': movimiento_id,
            'accion': 'create',
            'descripcion': f"Entrada de {data['cantidad']} unidades de {producto['nombre']}",
            'datos_nuevos': movimiento_data,
            'id_usuario': usuario_id
        })
        
        return movimiento_id
    
    @staticmethod
    def crear_salida(data: dict, usuario_id: int, localidad_id: int) -> int:
        """
        Registrar salida de stock
        VALIDA que haya stock suficiente
        
        Args:
            data (dict): {
                'id_producto': int,
                'cantidad': int,
                'lugar_origen': int,
                'motivo': str,
                'observaciones': str (opcional)
            }
        """
        # Validaciones
        MovimientoService._validate_movimiento_data(data, 'salida')
        
        # Verificar producto
        producto = ProductoDAO.get_by_id(data['id_producto'])
        if not producto:
            raise Exception("Producto no encontrado")
        
        # Verificar lugar
        lugar = LugarDAO.get_by_id(data['lugar_origen'])
        if not lugar:
            raise Exception("Lugar de origen no encontrado")
        
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
        
        # Crear movimiento
        movimiento_data = {
            'tipo': 'salida',
            'cantidad': data['cantidad'],
            'id_producto': data['id_producto'],
            'id_usuario': usuario_id,
            'id_localidad': localidad_id,
            'lugar_origen': data['lugar_origen'],
            'motivo': data.get('motivo', ''),
            'observaciones': data.get('observaciones', '')
        }
        
        movimiento_id = MovimientoDAO.create(movimiento_data)
        
        # ACTUALIZAR STOCK (restar)
        ProductoLocalidadDAO.restar_stock(
            data['id_producto'],
            data['lugar_origen'],
            data['cantidad']
        )
        
        # Registrar en auditoría
        AuditoriaDAO.create({
            'entidad': 'Movimiento',
            'id_entidad': movimiento_id,
            'accion': 'create',
            'descripcion': f"Salida de {data['cantidad']} unidades de {producto['nombre']}",
            'datos_nuevos': movimiento_data,
            'id_usuario': usuario_id
        })
        
        return movimiento_id
    
    @staticmethod
    def crear_transferencia(data: dict, usuario_id: int, localidad_id: int) -> int:
        """
        Transferir stock entre lugares
        
        Args:
            data (dict): {
                'id_producto': int,
                'cantidad': int,
                'lugar_origen': int,
                'lugar_destino': int,
                'motivo': str,
                'observaciones': str (opcional)
            }
        """
        # Validaciones
        MovimientoService._validate_movimiento_data(data, 'transferencia')
        
        # Verificar producto
        producto = ProductoDAO.get_by_id(data['id_producto'])
        if not producto:
            raise Exception("Producto no encontrado")
        
        # Verificar lugares
        lugar_origen = LugarDAO.get_by_id(data['lugar_origen'])
        lugar_destino = LugarDAO.get_by_id(data['lugar_destino'])
        
        if not lugar_origen:
            raise Exception("Lugar de origen no encontrado")
        if not lugar_destino:
            raise Exception("Lugar de destino no encontrado")
        
        if data['lugar_origen'] == data['lugar_destino']:
            raise Exception("El lugar origen y destino no pueden ser el mismo")
        
        # VALIDAR STOCK DISPONIBLE
        stock_disponible = ProductoLocalidadDAO.get_stock(
            data['id_producto'],
            data['lugar_origen']
        )
        
        if stock_disponible < data['cantidad']:
            raise Exception(
                f"Stock insuficiente en origen. Disponible: {stock_disponible}"
            )
        
        # Crear movimiento
        movimiento_data = {
            'tipo': 'transferencia',
            'cantidad': data['cantidad'],
            'id_producto': data['id_producto'],
            'id_usuario': usuario_id,
            'id_localidad': localidad_id,
            'lugar_origen': data['lugar_origen'],
            'lugar_destino': data['lugar_destino'],
            'motivo': data.get('motivo', ''),
            'observaciones': data.get('observaciones', '')
        }
        
        movimiento_id = MovimientoDAO.create(movimiento_data)
        
        # ACTUALIZAR STOCK (transferir)
        ProductoLocalidadDAO.transferir_stock(
            data['id_producto'],
            data['lugar_origen'],
            data['lugar_destino'],
            data['cantidad']
        )
        
        # Registrar en auditoría
        AuditoriaDAO.create({
            'entidad': 'Movimiento',
            'id_entidad': movimiento_id,
            'accion': 'create',
            'descripcion': (
                f"Transferencia de {data['cantidad']} unidades de {producto['nombre']} "
                f"de {lugar_origen['nombre']} a {lugar_destino['nombre']}"
            ),
            'datos_nuevos': movimiento_data,
            'id_usuario': usuario_id
        })
        
        return movimiento_id
    
    @staticmethod
    def crear_ajuste(data: dict, usuario_id: int, localidad_id: int) -> int:
        """
        Ajustar stock (inventario físico)
        
        Args:
            data (dict): {
                'id_producto': int,
                'lugar_id': int,
                'cantidad_nueva': int,
                'motivo': str,
                'observaciones': str (opcional)
            }
        """
        # Validaciones
        if 'cantidad_nueva' not in data or data['cantidad_nueva'] < 0:
            raise Exception("Cantidad nueva inválida")
        
        # Verificar producto y lugar
        producto = ProductoDAO.get_by_id(data['id_producto'])
        lugar = LugarDAO.get_by_id(data['lugar_id'])
        
        if not producto:
            raise Exception("Producto no encontrado")
        if not lugar:
            raise Exception("Lugar no encontrado")
        
        # Obtener stock actual
        stock_actual = ProductoLocalidadDAO.get_stock(
            data['id_producto'],
            data['lugar_id']
        )
        
        # Calcular diferencia
        diferencia = data['cantidad_nueva'] - stock_actual
        
        # Crear movimiento
        movimiento_data = {
            'tipo': 'ajuste',
            'cantidad': abs(diferencia),  # Valor absoluto
            'id_producto': data['id_producto'],
            'id_usuario': usuario_id,
            'id_localidad': localidad_id,
            'lugar_destino': data['lugar_id'] if diferencia > 0 else None,
            'lugar_origen': data['lugar_id'] if diferencia < 0 else None,
            'motivo': data.get('motivo', 'Ajuste de inventario'),
            'observaciones': (
                f"Stock anterior: {stock_actual}, "
                f"Stock nuevo: {data['cantidad_nueva']}, "
                f"Diferencia: {diferencia:+d}. "
                f"{data.get('observaciones', '')}"
            )
        }
        
        movimiento_id = MovimientoDAO.create(movimiento_data)
        
        # ACTUALIZAR STOCK (ajustar)
        ProductoLocalidadDAO.ajustar_stock(
            data['id_producto'],
            data['lugar_id'],
            data['cantidad_nueva'],
            data.get('motivo', '')
        )
        
        # Registrar en auditoría
        AuditoriaDAO.create({
            'entidad': 'Movimiento',
            'id_entidad': movimiento_id,
            'accion': 'ajuste',
            'descripcion': (
                f"Ajuste de inventario de {producto['nombre']} en {lugar['nombre']}: "
                f"{stock_actual} → {data['cantidad_nueva']} ({diferencia:+d})"
            ),
            'datos_anteriores': {'stock': stock_actual},
            'datos_nuevos': {'stock': data['cantidad_nueva']},
            'id_usuario': usuario_id
        })
        
        return movimiento_id
    
    @staticmethod
    def get_historial(producto_id=None, usuario_id=None, localidad_id=None, 
                      page=1, limit=20, tipo=None, fecha_desde=None, fecha_hasta=None):
        """Obtener historial de movimientos con filtros"""
        return MovimientoDAO.get_all(
            page=page,
            limit=limit,
            tipo=tipo,
            producto_id=producto_id,
            usuario_id=usuario_id,
            localidad_id=localidad_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
    
    @staticmethod
    def get_by_id(movimiento_id: int) -> dict:
        """Obtener un movimiento por ID"""
        return MovimientoDAO.get_by_id(movimiento_id)
    
    @staticmethod
    def get_ultimos(limit: int = 10) -> list:
        """Obtener los últimos movimientos"""
        return MovimientoDAO.get_ultimos(limit)
    
    @staticmethod
    def _validate_movimiento_data(data: dict, tipo: str):
        """Validar datos de movimiento según tipo"""
        # Campos requeridos básicos
        if 'id_producto' not in data or not data['id_producto']:
            raise Exception("Producto es requerido")
        
        if 'cantidad' not in data or data['cantidad'] <= 0:
            raise Exception("Cantidad debe ser mayor a 0")
        
        # Validaciones según tipo
        if tipo == 'entrada':
            if 'lugar_destino' not in data:
                raise Exception("Lugar de destino es requerido para entradas")
        
        elif tipo == 'salida':
            if 'lugar_origen' not in data:
                raise Exception("Lugar de origen es requerido para salidas")
        
        elif tipo == 'transferencia':
            if 'lugar_origen' not in data or 'lugar_destino' not in data:
                raise Exception("Lugar de origen y destino son requeridos para transferencias")