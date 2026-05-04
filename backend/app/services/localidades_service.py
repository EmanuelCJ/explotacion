"""
Servicio de Productos
Maneja lógica de negocio de productos e inventario
"""

from app.DAO.producto_DAO import ProductoDAO
from app.DAO.categoria_DAO import CategoriaDAO
from app.DAO.auditoria_DAO import AuditoriaDAO
from app.DAO.localidad_DAO import LocalidadDAO
from app.DAO.usuario_DAO import UsuarioDAO
from app.DAO.producto_localidad_DAO import ProductoLocalidadDAO
from app.utils.decoradores_auth import get_client_ip
from app.utils.generacion_codigo_producto import generar_codigo_producto


class LocalidadesService:
    
    @staticmethod
    def get_localidades():
        return LocalidadDAO.get_all()