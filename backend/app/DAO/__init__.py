"""
Módulo DAO - Data Access Objects
Sistema de Inventario - Aguas Rionegrinas

Importar todos los DAOs desde aquí para facilitar su uso
"""

from .usuario_DAO import UsuarioDAO
from .producto_DAO import ProductoDAO
from .localidad_DAO import LocalidadDAO
from .categoria_DAO import CategoriaDAO
from .lugar_DAO import LugarDAO
from .producto_localidad_DAO import ProductoLocalidadDAO
from .movimiento_DAO import MovimientoDAO
from .envio_DAO import EnvioDAO
from .auditoria_DAO import AuditoriaDAO
from .rol_permiso_DAO import RolDAO, PermisoDAO

__all__ = [
    'UsuarioDAO',
    'ProductoDAO',
    'LocalidadDAO',
    'CategoriaDAO',
    'LugarDAO',
    'ProductoLocalidadDAO',
    'MovimientoDAO',
    'EnvioDAO',
    'AuditoriaDAO',
    'RolDAO',
    'PermisoDAO'
]