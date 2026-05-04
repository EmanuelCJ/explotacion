"""
Router de Localiades
CRUD completo de productos con validación de permisos
"""

from flask import Blueprint, request, jsonify
from app.services.producto_service import ProductoService
from app.services.usuario_service import UsuarioService
from app.services.localidades_service import LocalidadesService
from app.middlewares.producto_validation import validate_producto_data
from app.utils.decoradores_auth import (
    jwt_required_cookie,
    require_permiso,
    require_role,
    get_current_user_id
)


localidades_bp = Blueprint('localidades', __name__)


@localidades_bp.route('/', methods=['GET'])
@jwt_required_cookie()
# @require_permiso('ver_localidades')
def get_localidad():

    localidades = LocalidadesService.get_localidades()

    return jsonify(localidades), 200
