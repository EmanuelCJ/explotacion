"""

Servicio de localidades

"""

from app.DAO.localidad_DAO import LocalidadDAO


class LocalidadesService:
    
    @staticmethod
    def get_localidades():
        return LocalidadDAO.get_all()