"""
Servicio de Autenticación
Maneja login, registro, validación de credenciales
"""

import bcrypt
from app.DAO.usuario_DAO import UsuarioDAO
from app.DAO.auditoria_DAO import AuditoriaDAO


class AuthService:
    """Servicio de autenticación y gestión de sesiones"""
    
    @staticmethod
    def authenticate(username: str, password: str, ip_address: str = None) -> dict:
        """
        Autenticar usuario con username y password
        
        Args:
            username: Username del usuario
            password: Password en texto plano
            ip_address: IP del usuario (opcional)
        
        Returns:
            dict: Datos del usuario si es válido, None si falla
        
        Raises:
            Exception: Si las credenciales son inválidas
        """
        # Buscar usuario por username
        usuario = UsuarioDAO.get_by_username(username)
        
        if not usuario:
            raise Exception("Usuario no encontrado")
        
        # Verificar que esté activo
        if not usuario['activo']:
            raise Exception("Usuario inactivo")
        
        # Verificar password
        if not AuthService.verify_password(password, usuario['password_hash']):
            # Registrar intento fallido en auditoría
            AuditoriaDAO.create({
                'entidad': 'Usuario',
                'id_entidad': usuario['id_usuario'],
                'accion': 'login',
                'descripcion': 'Intento de login fallido',
                'id_usuario': usuario['id_usuario'],
                'ip_address': ip_address
            })
            raise Exception("Contraseña incorrecta")
        
        # Actualizar último login
        UsuarioDAO.update_ultimo_login(usuario['id_usuario'])
        
        # Registrar login exitoso en auditoría
        AuditoriaDAO.create({
            'entidad': 'Usuario',
            'id_entidad': usuario['id_usuario'],
            'accion': 'login',
            'descripcion': f"Login exitoso: {username}",
            'id_usuario': usuario['id_usuario'],
            'ip_address': ip_address
        })
        
        # Obtener permisos del usuario
        permisos = UsuarioDAO.get_permisos(usuario['id_usuario'])
        usuario['permisos'] = [p['nombre'] for p in permisos]
        
        # Limpiar password_hash de la respuesta
        del usuario['password_hash']
        
        return usuario
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashear password con bcrypt
        
        Args:
            password: Password en texto plano
        
        Returns:
            str: Password hasheado
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verificar que el password coincida con el hash
        
        Args:
            password: Password en texto plano
            password_hash: Hash del password
        
        Returns:
            bool: True si coincide, False si no
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            print(f"Error verificando password: {e}")
            return False
    
    @staticmethod
    def change_password(usuario_id: int, password_actual: str, password_nuevo: str, admin_id: int = None) -> bool:
        """
        Cambiar contraseña de usuario
        
        Args:
            usuario_id: ID del usuario
            password_actual: Password actual (validar)
            password_nuevo: Nuevo password
            admin_id: ID del admin que hace el cambio (opcional)
        
        Returns:
            bool: True si se cambió correctamente
        """
        # Obtener usuario
        usuario = UsuarioDAO.get_by_id(usuario_id)
        if not usuario:
            raise Exception("Usuario no encontrado")
        
        # Si no es admin, verificar password actual
        if not admin_id:
            if not AuthService.verify_password(password_actual, usuario['password_hash']):
                raise Exception("Password actual incorrecto")
        
        # Validar nuevo password
        if len(password_nuevo) < 6:
            raise Exception("El password debe tener al menos 6 caracteres")
        
        # Hashear nuevo password
        nuevo_hash = AuthService.hash_password(password_nuevo)
        
        # Actualizar en BD
        success = UsuarioDAO.update_password(usuario_id, nuevo_hash)
        
        if success:
            # Registrar en auditoría
            AuditoriaDAO.create({
                'entidad': 'Usuario',
                'id_entidad': usuario_id,
                'accion': 'update',
                'descripcion': 'Cambio de contraseña',
                'id_usuario': admin_id if admin_id else usuario_id
            })
        
        return success
    
    @staticmethod
    def get_user_by_id(usuario_id: int) -> dict:
        """
        Obtener usuario por ID (sin password)
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            dict: Datos del usuario sin password
        """
        usuario = UsuarioDAO.get_by_id(usuario_id)
        
        if usuario and 'password_hash' in usuario:
            del usuario['password_hash']
        
        return usuario
    
    @staticmethod
    def validate_permissions(usuario_id: int, required_permission: str) -> bool:
        """
        Validar si un usuario tiene un permiso específico
        
        Args:
            usuario_id: ID del usuario
            required_permission: Nombre del permiso requerido
        
        Returns:
            bool: True si tiene el permiso, False si no
        """
        return UsuarioDAO.tiene_permiso(usuario_id, required_permission)
    
    @staticmethod
    def validate_any_permission(usuario_id: int, permissions: list) -> bool:
        """
        Validar si un usuario tiene AL MENOS UNO de los permisos
        
        Args:
            usuario_id: ID del usuario
            permissions: Lista de nombres de permisos
        
        Returns:
            bool: True si tiene alguno, False si no tiene ninguno
        """
        for permission in permissions:
            if UsuarioDAO.tiene_permiso(usuario_id, permission):
                return True
        return False
    
    @staticmethod
    def logout(usuario_id: int, ip_address: str = None) -> bool:
        """
        Registrar logout en auditoría
        
        Args:
            usuario_id: ID del usuario
            ip_address: IP del usuario (opcional)
        
        Returns:
            bool: True siempre
        """
        # Registrar logout en auditoría
        AuditoriaDAO.create({
            'entidad': 'Usuario',
            'id_entidad': usuario_id,
            'accion': 'logout',
            'descripcion': 'Cierre de sesión',
            'id_usuario': usuario_id,
            'ip_address': ip_address
        })
        
        return True