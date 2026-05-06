"""
Servicio de Roles
Maneja lógica de negocio de gestión de roles

"""

from app.DAO.rol_permiso_DAO import RolDAO


class RolesService:
    @staticmethod
    def get_roles():
        return RolDAO.get()