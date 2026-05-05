"""
Router de Localiades
CRUD completo de productos con validación de permisos
"""

from flask import Blueprint, request, jsonify
from app.services.localidades_service import LocalidadesService
from app.utils.decoradores_auth import (
    jwt_required_cookie,
)

localidades_bp = Blueprint('localidades', __name__)


@localidades_bp.route('/', methods=['GET'])
@jwt_required_cookie()
def get_localidad():
    localidades = LocalidadesService.get_localidades()
    return jsonify(localidades), 200
