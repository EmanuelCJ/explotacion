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


class ProductoService:

    """Servicio de gestión de productos"""

    @staticmethod
    def create(data: dict, usuario_id: int) -> int:
        """
        Crear un nuevo producto

        Args:
            data (dict): {
                'nombre': str,
                'codigo': str,
                'descripcion': str,
                'id_categoria': int,
                'costo': float (opcional),
                'unidad_medida': str (opcional),
                'stock_minimo': int
            }
            usuario_id: ID del usuario que crea el producto

        Returns:
            int: ID del producto creado
        """

        #obtener la localidad del usuario que crea el producto
        usuario = UsuarioDAO.get_by_id(usuario_id)
        localidad = LocalidadDAO.get_by_nombre(usuario.get('localidad_nombre'))

        # Verificar que existe la categoría
        categoria = CategoriaDAO.get_by_id(data['id_categoria'])
        if not categoria:
            raise Exception("Categoría no encontrada")

        # Verificar que la categoría esté activa
        if not categoria['activo']:
            raise Exception("La categoría está inactiva")

        #crear codigo unicos a partir del nombre del producto y el nombre de la categoria
        data['codigo'] =  generar_codigo_producto(data['nombre'], categoria['nombre'])

        # Verificar que no exista el código
        if data.get('codigo') and ProductoDAO.exists_codigo(codigo=data['codigo']):
            raise Exception(f"El código '{data['codigo']}' ya existe")
        
        # verificar que no exista un producto con el mismo nombre en la misma categoría en esa| localidad y lugar
        if ProductoDAO.exist_producto(nombre=data['nombre'], id_categoria=data['id_categoria'], id_localidad=localidad['id_localidad'], id_lugar=data['id_lugar']):
            raise Exception(f"Ya existe un producto con el nombre '{data['nombre']}' en la categoría seleccionada")
        
        #verificar que exista la localidad
        if localidad is None:
            raise Exception("La localidad no existe")
        
        # Crear producto
        producto_id = ProductoDAO.create(data)

        
        if producto_id:

            # crear un a consulta para registrar localidad/producto
            ProductoLocalidadDAO.init_stock(
                producto_id=producto_id, 
                lugar_id=data['id_lugar'], 
                localidad_id=localidad['id_localidad'],
                cantidad=data['stock_minimo'])

            # Registrar en auditoría
            AuditoriaDAO.create({
                'entidad': 'Producto',
                'id_entidad': producto_id,
                'accion': 'create',
                'descripcion': f"Producto creado: {data['nombre']}",
                'datos_nuevos': {
                    'nombre': data['nombre'],
                    'codigo': data.get('codigo'),
                    'categoria_id': data['id_categoria']
                },
                'id_usuario': usuario_id,
                'ip_address': get_client_ip(),
                'user_agent': usuario['username']
            })

        return producto_id
    
    @staticmethod
    def get_stock_en_localidad(localidad_nombre: str) -> dict:
        """Obtener stock de todos los productos en una localidad"""
        return ProductoDAO.get_stock_en_localidad(localidad_nombre)

    @staticmethod
    def get_all(page=1, limit=20, categoria_id=None, activo=None, search=None):
        """Obtener todos los productos con filtros"""
        result = ProductoDAO.get_all(page, limit, categoria_id, activo, search)

        # Agregar stock total a cada producto
        for producto in result['productos']:
            producto['stock_total'] = ProductoDAO.get_stock_total(producto['id_producto'])

        return result

    @staticmethod
    def get_by_id(producto_id: int) -> dict:
        """Obtener producto por ID con información completa"""
        producto = ProductoDAO.get_by_id(producto_id)

        if not producto:
            return None

        # Agregar stock total
        producto['stock_total'] = ProductoDAO.get_stock_total(producto_id)

        # Agregar stock por localidad
        producto['stock_por_localidad'] = ProductoDAO.get_stock_por_localidad(producto_id)

        return producto

    @staticmethod
    def update(producto_id: int, data: dict, usuario_id: int) -> bool:
        """
        Actualizar producto

        Args:
            producto_id: ID del producto
            data: Datos a actualizar
            usuario_id: ID del usuario que actualiza

        Returns:
            bool: True si se actualizó
        """
        # Obtener producto actual
        producto_actual = ProductoDAO.get_by_id(producto_id)
        if not producto_actual:
            raise Exception("Producto no encontrado")

        # Validar código si se está cambiando
        if 'codigo' in data and data['codigo']:
            if ProductoDAO.exists_codigo(data['codigo'], producto_id):
                raise Exception(f"El código '{data['codigo']}' ya existe")

        # Validar categoría si se está cambiando
        if 'id_categoria' in data:
            categoria = CategoriaDAO.get_by_id(data['id_categoria'])
            if not categoria:
                raise Exception("Categoría no encontrada")

        # Actualizar
        success = ProductoDAO.update(producto_id, data)

        if success:
            # Registrar en auditoría
            AuditoriaDAO.create({
                'entidad': 'Producto',
                'id_entidad': producto_id,
                'accion': 'update',
                'descripcion': f"Producto actualizado: {producto_actual['nombre']}",
                'datos_anteriores': {
                    'nombre': producto_actual['nombre'],
                    'codigo': producto_actual.get('codigo'),
                    'costo': producto_actual.get('costo')
                },
                'datos_nuevos': data,
                'id_usuario': usuario_id
            })

        return success

    @staticmethod
    def delete(producto_id: int, usuario_id: int) -> bool:
        """
        Eliminar (desactivar) producto

        Args:
            producto_id: ID del producto
            usuario_id: ID del usuario que elimina
        """
        producto = ProductoDAO.get_by_id(producto_id)
        if not producto:
            raise Exception("Producto no encontrado")

        # Verificar que no tenga stock
        stock_total = ProductoDAO.get_stock_total(producto_id)
        if stock_total > 0:
            raise Exception(f"No se puede eliminar. El producto tiene stock: {stock_total} unidades")

        success = ProductoDAO.delete(producto_id)

        if success:
            # Registrar en auditoría
            AuditoriaDAO.create({
                'entidad': 'Producto',
                'id_entidad': producto_id,
                'accion': 'delete',
                'descripcion': f"Producto eliminado: {producto['nombre']}",
                'id_usuario': usuario_id
            })

        return success

    @staticmethod
    def get_stock_por_localidad(producto_id: int) -> list:
        """Obtener stock del producto en cada localidad"""
        return ProductoDAO.get_stock_por_localidad(producto_id)

    @staticmethod
    def get_productos_stock_bajo() -> list:
        """Obtener productos con stock por debajo del mínimo"""
        return ProductoDAO.get_productos_stock_bajo()

    @staticmethod
    def verificar_stock_minimo(producto_id: int) -> dict:
        """
        Verificar si un producto está por debajo del stock mínimo

        Returns:
            dict: {
                'por_debajo': bool,
                'stock_actual': int,
                'stock_minimo': int,
                'diferencia': int
            }
        """
        producto = ProductoDAO.get_by_id(producto_id)
        if not producto:
            raise Exception("Producto no encontrado")

        stock_actual = ProductoDAO.get_stock_total(producto_id)
        stock_minimo = producto['stock_minimo']

        return {
            'por_debajo': stock_actual < stock_minimo,
            'stock_actual': stock_actual,
            'stock_minimo': stock_minimo,
            'diferencia': stock_minimo - stock_actual
        }

    #esta función es para validar los datos de entrada al crear o actualizar un producto
    @staticmethod
    def _validate_product_data(data: dict):

        """Validar datos de producto"""
        # Campos requeridos
        required = ['nombre', 'id_categoria']
        for field in required:
            if field not in data or not data[field]:
                raise Exception(f"Campo requerido: {field}")

        # Validar nombre
        if len(data['nombre']) < 3:
            raise Exception("El nombre debe tener al menos 3 caracteres")

        # Validar costo si está presente
        if 'costo' in data and data['costo'] is not None:
            if data['costo'] < 0:
                raise Exception("El costo no puede ser negativo")

        # Validar stock_minimo si está presente
        if 'stock_minimo' in data and data['stock_minimo'] is not None:
            if data['stock_minimo'] < 0:
                raise Exception("El stock mínimo no puede ser negativo")
            
