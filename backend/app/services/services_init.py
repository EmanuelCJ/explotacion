"""
Módulo Services - Lógica de Negocio
Sistema de Inventario - Aguas Rionegrinas
"""

from .auth_service import AuthService
from .usuario_service import UsuarioService
from .producto_service import ProductoService
from .movimiento_service import MovimientoService
from .envio_service import EnvioService

__all__ = [
    'AuthService',
    'UsuarioService',
    'ProductoService',
    'MovimientoService',
    'EnvioService',
    'AuditoriaService',
    'CategoriaService',
    'LocalidadService',
    'LugarService'
]


# ========================================
# AUDITORIA SERVICE
# ========================================
from app.DAO.auditoria_DAO import AuditoriaDAO

class AuditoriaService:
    """Servicio de consulta de auditoría"""
    
    @staticmethod
    def get_all(page=1, limit=50, **filters):
        """Obtener todos los registros de auditoría"""
        return AuditoriaDAO.get_all(page=page, limit=limit, **filters)
    
    @staticmethod
    def get_by_usuario(usuario_id: int, page=1, limit=50):
        """Obtener auditoría de un usuario"""
        return AuditoriaDAO.get_by_usuario(usuario_id, page, limit)
    
    @staticmethod
    def get_by_entidad(entidad: str, id_entidad: int):
        """Obtener historial de una entidad"""
        return AuditoriaDAO.get_by_entidad(entidad, id_entidad)
    
    @staticmethod
    def get_actividad_reciente(limit: int = 20):
        """Obtener actividad reciente del sistema"""
        return AuditoriaDAO.get_actividad_reciente(limit)
    
    @staticmethod
    def get_estadisticas(fecha_desde=None, fecha_hasta=None):
        """Obtener estadísticas de auditoría"""
        return {
            'por_accion': AuditoriaDAO.count_por_accion(fecha_desde, fecha_hasta),
            'por_usuario': AuditoriaDAO.count_por_usuario(fecha_desde, fecha_hasta)
        }


# ========================================
# CATEGORIA SERVICE
# ========================================
from app.DAO.categoria_DAO import CategoriaDAO

class CategoriaService:
    """Servicio de gestión de categorías"""
    
    @staticmethod
    def create(data: dict, usuario_id: int) -> int:
        """Crear categoría"""
        # Validar que no exista el código
        if data.get('codigo') and CategoriaDAO.exists_codigo(data['codigo']):
            raise Exception(f"El código '{data['codigo']}' ya existe")
        
        categoria_id = CategoriaDAO.create(data)
        
        # Auditoría
        AuditoriaDAO.create({
            'entidad': 'Categoria',
            'id_entidad': categoria_id,
            'accion': 'create',
            'descripcion': f"Categoría creada: {data['nombre']}",
            'id_usuario': usuario_id
        })
        
        return categoria_id
    
    @staticmethod
    def get_all(activo=None):
        """Obtener todas las categorías"""
        return CategoriaDAO.get_all(activo)
    
    @staticmethod
    def get_by_id(categoria_id: int):
        """Obtener categoría por ID"""
        return CategoriaDAO.get_by_id(categoria_id)
    
    @staticmethod
    def update(categoria_id: int, data: dict, usuario_id: int) -> bool:
        """Actualizar categoría"""
        success = CategoriaDAO.update(categoria_id, data)
        
        if success:
            AuditoriaDAO.create({
                'entidad': 'Categoria',
                'id_entidad': categoria_id,
                'accion': 'update',
                'descripcion': 'Categoría actualizada',
                'id_usuario': usuario_id
            })
        
        return success
    
    @staticmethod
    def delete(categoria_id: int, usuario_id: int) -> bool:
        """Eliminar categoría (soft delete)"""
        # Verificar que no tenga productos
        count = CategoriaDAO.count_productos(categoria_id)
        if count > 0:
            raise Exception(f"No se puede eliminar. Tiene {count} productos asociados")
        
        success = CategoriaDAO.delete(categoria_id)
        
        if success:
            AuditoriaDAO.create({
                'entidad': 'Categoria',
                'id_entidad': categoria_id,
                'accion': 'delete',
                'descripcion': 'Categoría eliminada',
                'id_usuario': usuario_id
            })
        
        return success


# ========================================
# LOCALIDAD SERVICE
# ========================================
from app.DAO.localidad_DAO import LocalidadDAO

class LocalidadService:
    """Servicio de gestión de localidades"""
    
    @staticmethod
    def create(data: dict, usuario_id: int) -> int:
        """Crear localidad"""
        # Validar que no exista el nombre
        if LocalidadDAO.exists_nombre(data['nombre']):
            raise Exception(f"La localidad '{data['nombre']}' ya existe")
        
        localidad_id = LocalidadDAO.create(data)
        
        # Auditoría
        AuditoriaDAO.create({
            'entidad': 'Localidad',
            'id_entidad': localidad_id,
            'accion': 'create',
            'descripcion': f"Localidad creada: {data['nombre']}",
            'id_usuario': usuario_id
        })
        
        return localidad_id
    
    @staticmethod
    def get_all(activo=None):
        """Obtener todas las localidades"""
        return LocalidadDAO.get_all(activo)
    
    @staticmethod
    def get_by_id(localidad_id: int):
        """Obtener localidad por ID"""
        return LocalidadDAO.get_by_id(localidad_id)
    
    @staticmethod
    def get_con_lugares(localidad_id: int):
        """Obtener localidad con sus lugares"""
        return LocalidadDAO.get_con_lugares(localidad_id)
    
    @staticmethod
    def update(localidad_id: int, data: dict, usuario_id: int) -> bool:
        """Actualizar localidad"""
        success = LocalidadDAO.update(localidad_id, data)
        
        if success:
            AuditoriaDAO.create({
                'entidad': 'Localidad',
                'id_entidad': localidad_id,
                'accion': 'update',
                'descripcion': 'Localidad actualizada',
                'id_usuario': usuario_id
            })
        
        return success
    
    @staticmethod
    def delete(localidad_id: int, usuario_id: int) -> bool:
        """Eliminar localidad (soft delete)"""
        # Verificar que no tenga lugares
        count = LocalidadDAO.count_lugares(localidad_id)
        if count > 0:
            raise Exception(f"No se puede eliminar. Tiene {count} lugares asociados")
        
        success = LocalidadDAO.delete(localidad_id)
        
        if success:
            AuditoriaDAO.create({
                'entidad': 'Localidad',
                'id_entidad': localidad_id,
                'accion': 'delete',
                'descripcion': 'Localidad eliminada',
                'id_usuario': usuario_id
            })
        
        return success


# ========================================
# LUGAR SERVICE
# ========================================
from app.DAO.lugar_DAO import LugarDAO

class LugarService:
    """Servicio de gestión de lugares"""
    
    @staticmethod
    def create(data: dict, usuario_id: int) -> int:
        """Crear lugar"""
        # Verificar que existe la localidad
        localidad = LocalidadDAO.get_by_id(data['id_localidad'])
        if not localidad:
            raise Exception("Localidad no encontrada")
        
        lugar_id = LugarDAO.create(data)
        
        # Auditoría
        AuditoriaDAO.create({
            'entidad': 'Lugar',
            'id_entidad': lugar_id,
            'accion': 'create',
            'descripcion': f"Lugar creado: {data['nombre']}",
            'id_usuario': usuario_id
        })
        
        return lugar_id
    
    @staticmethod
    def get_all(localidad_id=None, tipo=None, activo=None):
        """Obtener todos los lugares"""
        return LugarDAO.get_all(localidad_id, tipo, activo)
    
    @staticmethod
    def get_by_id(lugar_id: int):
        """Obtener lugar por ID"""
        return LugarDAO.get_by_id(lugar_id)
    
    @staticmethod
    def get_by_localidad(localidad_id: int):
        """Obtener lugares de una localidad"""
        return LugarDAO.get_by_localidad(localidad_id)
    
    @staticmethod
    def update(lugar_id: int, data: dict, usuario_id: int) -> bool:
        """Actualizar lugar"""
        success = LugarDAO.update(lugar_id, data)
        
        if success:
            AuditoriaDAO.create({
                'entidad': 'Lugar',
                'id_entidad': lugar_id,
                'accion': 'update',
                'descripcion': 'Lugar actualizado',
                'id_usuario': usuario_id
            })
        
        return success
    
    @staticmethod
    def delete(lugar_id: int, usuario_id: int) -> bool:
        """Eliminar lugar (soft delete)"""
        success = LugarDAO.delete(lugar_id)
        
        if success:
            AuditoriaDAO.create({
                'entidad': 'Lugar',
                'id_entidad': lugar_id,
                'accion': 'delete',
                'descripcion': 'Lugar eliminado',
                'id_usuario': usuario_id
            })
        
        return success