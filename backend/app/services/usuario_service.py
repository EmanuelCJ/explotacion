"""
Servicio de Usuarios
Maneja lógica de negocio de gestión de usuarios
"""

from app.DAO.usuario_DAO import UsuarioDAO
from app.DAO.localidad_DAO import LocalidadDAO
from app.DAO.auditoria_DAO import AuditoriaDAO
from app.services.auth_service import AuthService
from app.utils.decoradores_auth import get_client_ip
from app.DAO.usuario_DAO import UsuarioDAO
import re


class UsuarioService:
    """Servicio de gestión de usuarios"""
    
    @staticmethod
    def create(data: dict, admin_id: int) -> int:
        """
        Crear un nuevo usuario
        
        Args:
            data (dict): {
                'nombre': str,
                'apellido': str,
                'username': str,
                'email': str,
                'password': str,
                'legajo': str (opcional),
                'id_localidad': int,
                'id_rol': int
            }
            admin_id: ID del administrador que crea el usuario
        
        Returns:
            int: ID del usuario creado
        """
        # Validaciones
        UsuarioService._validate_user_data(data)
        
        # Verificar que no exista el username
        if UsuarioDAO.exists_username(data['username']):
            raise Exception(f"El username '{data['username']}' ya existe")
        
        # Verificar que no exista el email
        if data.get('email') and UsuarioDAO.exists_email(data['email']):
            raise Exception(f"El email '{data['email']}' ya existe")
        
        # Verificar que existe la localidad
        localidad = LocalidadDAO.get_by_id(data['id_localidad'])
        if not localidad:
            raise Exception("Localidad no encontrada")
        
        # Hashear password
        password_hash = AuthService.hash_password(data['password'])
        
        # Preparar datos para insertar
        user_data = {
            'nombre': data['nombre'],
            'apellido': data['apellido'],
            'username': data['username'],
            'email': data.get('email'),
            'password_hash': password_hash,
            'legajo': data.get('legajo'),
            'id_localidad': data['id_localidad']
        }
        
        # Crear usuario
        usuario_id = UsuarioDAO.create(user_data)
        
        # Asignar rol
        if usuario_id > 0:
            UsuarioDAO.asignar_rol(usuario_id, data['id_rol'], admin_id)
        

        # Obtener IP del cliente para la auditoría
        ip_user = get_client_ip()

        # Obtener User Agent para la auditoría osea quien crea el usuario
        user_agent = UsuarioDAO.username(admin_id)

        # Registrar en auditoría
        AuditoriaDAO.create({
            'entidad': 'Usuario',
            'id_entidad': usuario_id,
            'accion': 'create',
            'descripcion': f"Usuario creado: {data['username']}",
            'ip_address': ip_user,
            'user_agent': user_agent,
            'datos_nuevos': {
                'nombre': data['nombre'],
                'apellido': data['apellido'],
                'username': data['username'],
                'localidad_id': data['id_localidad']
            },
            'id_usuario': admin_id
        })

        return usuario_id
    
    @staticmethod
    def get_all(page=1, limit=20, activo=None):
        """Obtener todos los usuarios con paginación"""
        return UsuarioDAO.get_all(page, limit, activo)
    
    @staticmethod
    def get_by_id(usuario_id: int) -> dict:
        """Obtener usuario por ID (sin password)"""
        usuario = UsuarioDAO.get_by_id(usuario_id)
        if usuario and 'password_hash' in usuario:
            del usuario['password_hash']
        return usuario
    
    @staticmethod
    def update(usuario_id: int, data: dict, admin_id: int) -> bool:
        """
        Actualizar usuario
        
        Args:
            usuario_id: ID del usuario a actualizar
            data: Datos a actualizar
            admin_id: ID del admin que actualiza
        
        Returns:
            bool: True si se actualizó
        """
        # Obtener usuario actual
        usuario_actual = UsuarioDAO.get_by_id(usuario_id)
        if not usuario_actual:
            raise Exception("Usuario no encontrado")
        
        # Validar campos si están presentes
        if 'email' in data and data['email']:
            if not UsuarioService._validate_email(data['email']):
                raise Exception("Email inválido")
            
            # Verificar que no exista otro usuario con ese email
            if UsuarioDAO.exists_email(data['email']):
                usuario_email = UsuarioDAO.get_by_email(data['email'])
                if usuario_email['id_usuario'] != usuario_id:
                    raise Exception("El email ya está en uso")
        
        # Actualizar
        success = UsuarioDAO.update(usuario_id, data)
        
        if success:
            # Registrar en auditoría
            AuditoriaDAO.create({
                'entidad': 'Usuario',
                'id_entidad': usuario_id,
                'accion': 'update',
                'descripcion': f"Usuario actualizado: {usuario_actual['username']}",
                'datos_anteriores': {
                    'nombre': usuario_actual['nombre'],
                    'apellido': usuario_actual['apellido'],
                    'email': usuario_actual.get('email')
                },
                'datos_nuevos': data,
                'id_usuario': admin_id
            })
        
        return success
    
    @staticmethod
    def delete(usuario_id: int, admin_id: int) -> bool:
        """
        Eliminar (desactivar) usuario
        
        Args:
            usuario_id: ID del usuario
            admin_id: ID del admin que elimina
        """
        usuario = UsuarioDAO.get_by_id(usuario_id)
        if not usuario:
            raise Exception("Usuario no encontrado")
        
        # No permitir eliminar el propio usuario
        if int(usuario_id) == int(admin_id):
            raise Exception("No puedes eliminarte a ti mismo")
        
        username = UsuarioDAO.username(admin_id)
        ip_user = get_client_ip()
        
        success = UsuarioDAO.delete(usuario_id)
        
        if success:
            # Registrar en auditoría
            AuditoriaDAO.create({
                'entidad': 'Usuario',
                'id_entidad': usuario_id,
                'accion': 'delete',
                'descripcion': f"Usuario eliminado: {usuario['username']}",
                'id_usuario': admin_id,
                'user_agent': username,
                'ip_address': ip_user,
                'datos_anteriores': {
                    'nombre': usuario['nombre'],
                    'apellido': usuario['apellido'],
                    'username': usuario['username']
                },
                'datos_nuevos': {
                    'el usuario fue eliminado y no tiene datos nuevos'
                }
            })
        
        return success
    
    @staticmethod
    def asignar_rol(usuario_id: int, rol_id: int, admin_id: int) -> bool:
        """Asignar rol a usuario"""
        usuario = UsuarioDAO.get_by_id(usuario_id)
        if not usuario:
            raise Exception("Usuario no encontrado")
        
        rol_viejo = UsuarioDAO.get_rol(usuario_id)
        ip_user = get_client_ip()
        username = UsuarioDAO.username(admin_id)

        success = UsuarioDAO.asignar_rol(usuario_id, rol_id, admin_id)
        
        if success:
            # Registrar en auditoría
            AuditoriaDAO.create({
                'entidad': 'Usuario',
                'id_entidad': usuario_id,
                'accion': 'update',
                'datos_anteriores': {'rol': rol_viejo if rol_viejo is not None else "sin rol"},
                'descripcion': f"Rol asignado al usuario {usuario['username']}",
                'datos_nuevos': {'rol_id': UsuarioDAO.get_rol(usuario_id)},
                'id_usuario': admin_id,
                'user_agent': username,
                'ip_address': ip_user
            })
        
        return success
    
    @staticmethod
    def quitar_rol(usuario_id: int, admin_id: int) -> bool:
        """Quitar rol de usuario"""
        
        # 🚨 Evitar que el usuario elimine su propio rol
        if int(usuario_id) == int(admin_id):
            raise Exception("No puedes quitar tu propio rol")

        usuario = UsuarioDAO.get_by_id(usuario_id)

        if not usuario:
            raise Exception("Usuario no encontrado")

        rol_viejo = UsuarioDAO.get_rol(usuario_id)
        ip_user = get_client_ip()

        success = UsuarioDAO.quitar_rol(usuario_id)
        
        if success:
            AuditoriaDAO.create({
            'entidad': 'Usuario',
            'id_entidad': usuario_id,
            'accion': 'update',
            'descripcion': f"Rol removido del usuario {usuario['username']}",
            'datos_anteriores': {'rol': rol_viejo},
            'datos_nuevos': {'rol_id': "sin rol"},
            'id_usuario': admin_id,
            'user_agent': UsuarioDAO.username(admin_id),
            'ip_address': ip_user
            })

        return success
    
    @staticmethod
    def _validate_user_data(data: dict):
        """Validar datos de usuario"""
        # Campos requeridos
        required = ['nombre', 'apellido', 'username', 'password', 'id_localidad']
        for field in required:
            if field not in data or not data[field]:
                raise Exception(f"Campo requerido: {field}")
        
        # Validar username (solo alfanumérico y _)
        if not re.match(r'^[a-zA-Z0-9_]{3,50}$', data['username']):
            raise Exception("Username inválido (3-50 caracteres, solo letras, números y _)")
        
        # Validar password
        if len(data['password']) < 6:
            raise Exception("El password debe tener al menos 6 caracteres")
        
        # Validar email si está presente
        if data.get('email') and not UsuarioService._validate_email(data['email']):
            raise Exception("Email inválido")
        
        #validar id_localidad que sea un entero
        if not isinstance(data['id_localidad'], int):
            raise Exception("id_localidad debe ser un número entero")
        
        #valida que id_rol sea un entero si está presente
        if 'id_rol' not in data:
            raise Exception("Campo requerido: id_rol")

        if not isinstance(data['id_rol'], int):
            raise Exception("id_rol debe ser un número entero")
    
    @staticmethod
    def _validate_email(email: str) -> bool:
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    

    @staticmethod
    def activar_usuario(usuario_id: int, admin_id: int) -> bool:
        """Activar usuario"""
        usuario = UsuarioDAO.get_by_id(usuario_id)
        if not usuario:
            raise Exception("Usuario no encontrado")

        if int(usuario_id) == int(admin_id):
            raise Exception("No es necesario activarte a ti mismo")
        
        ip_user = get_client_ip()
        username = UsuarioDAO.username(admin_id)
        
        success = UsuarioDAO.activar_usuario(usuario_id)
        
        if success:
            # Registrar en auditoría
            AuditoriaDAO.create({
                'entidad': 'Usuario',
                'id_entidad': usuario_id,
                'accion': 'update',
                'descripcion': f"Usuario activado: {usuario['username']}",
                'id_usuario': admin_id,
                'user_agent': username,
                'ip_address': ip_user
            })
        
        return success
    
    @staticmethod
    def desactivar_usuario(usuario_id: int, admin_id: int) -> bool:
        """Desactivar usuario"""
        usuario = UsuarioDAO.get_by_id(usuario_id)
        if not usuario:
            raise Exception("Usuario no encontrado")
        
        # No permitir desactivar el propio usuario
        if int(usuario_id) == int(admin_id):
            raise Exception("No puedes desactivarte a ti mismo")
        
        ip_user = get_client_ip()
        username = UsuarioDAO.username(admin_id)

        success = UsuarioDAO.desactivar_usuario(usuario_id)
        
        if success:
            # Registrar en auditoría
            AuditoriaDAO.create({
                'entidad': 'Usuario',
                'id_entidad': usuario_id,
                'accion': 'update',
                'descripcion': f"Usuario desactivado: {usuario['username']}",
                'id_usuario': admin_id,
                'user_agent': username,
                'ip_address': ip_user
            })
        
        return success