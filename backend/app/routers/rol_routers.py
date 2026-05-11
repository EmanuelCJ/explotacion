"""Roles de Usuarios - Solo para Admin"""

from flask import Blueprint, request, jsonify
from app.services.roles_service import RolesService
from app.utils.decoradores_auth import (
    jwt_required_cookie,
    require_permiso,
    require_role
)

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/', methods=['GET'])
@jwt_required_cookie()
@require_role('admin','maestro')
@require_permiso('ver_usuarios')
def get_usuarios():

    """Listar roles del sistema"""
    
    roles = RolesService.get_roles()
    return jsonify(roles), 200