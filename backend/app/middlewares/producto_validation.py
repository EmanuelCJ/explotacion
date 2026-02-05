"""
Decorador de validación para endpoints de Productos
Protege contra SQL injection y valida formato de datos
"""

from functools import wraps
from flask import request, jsonify
import re
from decimal import Decimal, InvalidOperation


def validate_producto_data(is_update=False):
    """
    Valida datos de creación/actualización de productos
    
    Validaciones:
    - Nombre: string 3-200 caracteres, sin caracteres especiales peligrosos
    - Código: alfanumérico, 3-50 caracteres
    - Descripción: máximo 1000 caracteres
    - Precio/Costo: decimal positivo, máximo 2 decimales
    - ID Categoría: entero positivo
    - Stock mínimo: entero >= 0
    - Unidad medida: string válido
    - Protección contra SQL injection
    
    Args:
        is_update (bool): True para PUT (campos opcionales), False para POST (campos requeridos)
    
    Usage:
        @producto_bp.route('/', methods=['POST'])
        @jwt_required_cookie()
        @require_permiso('crear_productos')
        @validate_producto_data()
        def create_producto():
            ...
        
        @producto_bp.route('/<int:id>', methods=['PUT'])
        @jwt_required_cookie()
        @require_permiso('editar_productos')
        @validate_producto_data(is_update=True)
        def update_producto(id):
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json()
                
                # Validar que venga JSON
                if not data:
                    return jsonify({
                        'error': 'Datos faltantes',
                        'detail': 'El body debe contener JSON válido'
                    }), 400
                
                # ===== VALIDAR NOMBRE =====
                if 'nombre' in data:
                    nombre = data.get('nombre')
                    
                    # Validar tipo
                    if not isinstance(nombre, str):
                        return jsonify({
                            'error': 'Nombre inválido',
                            'detail': 'El nombre debe ser un string'
                        }), 400
                    
                    # Sanitizar y validar longitud
                    nombre = nombre.strip()
                    if len(nombre) < 3 or len(nombre) > 200:
                        return jsonify({
                            'error': 'Nombre inválido',
                            'detail': 'El nombre debe tener entre 3 y 200 caracteres'
                        }), 400
                    
                    # Validar caracteres permitidos (letras, números, espacios, guiones, paréntesis)
                    if not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\(\)\.\/]+$', nombre):
                        return jsonify({
                            'error': 'Nombre inválido',
                            'detail': 'El nombre contiene caracteres no permitidos'
                        }), 400
                    
                    # Protección SQL injection
                    if _tiene_patron_sql_injection(nombre):
                        return jsonify({
                            'error': 'Datos sospechosos detectados',
                            'detail': 'El nombre contiene patrones no permitidos'
                        }), 400
                    
                    data['nombre'] = nombre
                
                elif not is_update:
                    # Campo requerido para creación
                    return jsonify({
                        'error': 'Campo requerido',
                        'detail': 'El nombre es obligatorio'
                    }), 400
                
                # ===== VALIDAR CÓDIGO =====
                if 'codigo' in data:
                    codigo = data.get('codigo')
                    
                    if not isinstance(codigo, str):
                        return jsonify({
                            'error': 'Código inválido',
                            'detail': 'El código debe ser un string'
                        }), 400
                    
                    codigo = codigo.strip().upper()  # Normalizar a mayúsculas
                    
                    if len(codigo) < 3 or len(codigo) > 50:
                        return jsonify({
                            'error': 'Código inválido',
                            'detail': 'El código debe tener entre 3 y 50 caracteres'
                        }), 400
                    
                    # Solo alfanuméricos y guiones
                    if not re.match(r'^[A-Z0-9\-]+$', codigo):
                        return jsonify({
                            'error': 'Código inválido',
                            'detail': 'El código solo puede contener letras, números y guiones'
                        }), 400
                    
                    if _tiene_patron_sql_injection(codigo):
                        return jsonify({
                            'error': 'Datos sospechosos detectados',
                            'detail': 'El código contiene patrones no permitidos'
                        }), 400
                    
                    data['codigo'] = codigo
                
                elif not is_update:
                    return jsonify({
                        'error': 'Campo requerido',
                        'detail': 'El código es obligatorio'
                    }), 400
                
                # ===== VALIDAR DESCRIPCIÓN =====
                if 'descripcion' in data:
                    descripcion = data.get('descripcion')
                    
                    if descripcion is not None:  # Puede ser None o vacío
                        if not isinstance(descripcion, str):
                            return jsonify({
                                'error': 'Descripción inválida',
                                'detail': 'La descripción debe ser un string'
                            }), 400
                        
                        descripcion = descripcion.strip()
                        
                        if len(descripcion) > 1000:
                            return jsonify({
                                'error': 'Descripción demasiado larga',
                                'detail': 'La descripción no puede exceder 1000 caracteres'
                            }), 400
                        
                        # Permitir más caracteres en descripción pero validar SQL injection
                        if _tiene_patron_sql_injection(descripcion):
                            return jsonify({
                                'error': 'Datos sospechosos detectados',
                                'detail': 'La descripción contiene patrones no permitidos'
                            }), 400
                        
                        data['descripcion'] = descripcion
                
                # ===== VALIDAR PRECIO/COSTO =====
                for campo in ['precio', 'costo', 'precio_venta']:
                    if campo in data:
                        valor = data.get(campo)
                        
                        if valor is not None:
                            try:
                                # Convertir a Decimal para validación precisa
                                if isinstance(valor, str):
                                    valor_decimal = Decimal(valor)
                                else:
                                    valor_decimal = Decimal(str(valor))
                                
                                # Validar que sea positivo
                                if valor_decimal < 0:
                                    return jsonify({
                                        'error': f'{campo.capitalize()} inválido',
                                        'detail': f'El {campo} debe ser un valor positivo'
                                    }), 400
                                
                                # Validar máximo 2 decimales
                                if valor_decimal.as_tuple().exponent < -2:
                                    return jsonify({
                                        'error': f'{campo.capitalize()} inválido',
                                        'detail': f'El {campo} solo puede tener hasta 2 decimales'
                                    }), 400
                                
                                # Validar rango máximo (evitar valores absurdos)
                                if valor_decimal > Decimal('999999999.99'):
                                    return jsonify({
                                        'error': f'{campo.capitalize()} inválido',
                                        'detail': f'El {campo} excede el valor máximo permitido'
                                    }), 400
                                
                                data[campo] = float(valor_decimal)
                                
                            except (InvalidOperation, ValueError):
                                return jsonify({
                                    'error': f'{campo.capitalize()} inválido',
                                    'detail': f'El {campo} debe ser un número válido'
                                }), 400
                        
                        elif not is_update and campo in ['precio', 'costo']:
                            # Precio/Costo requeridos en creación
                            return jsonify({
                                'error': 'Campo requerido',
                                'detail': f'El {campo} es obligatorio'
                            }), 400
                
                # ===== VALIDAR ID CATEGORÍA =====
                if 'id_categoria' in data:
                    id_categoria = data.get('id_categoria')
                    
                    if not isinstance(id_categoria, int) or id_categoria <= 0:
                        return jsonify({
                            'error': 'Categoría inválida',
                            'detail': 'El id_categoria debe ser un entero positivo'
                        }), 400
                
                elif not is_update:
                    return jsonify({
                        'error': 'Campo requerido',
                        'detail': 'La categoría es obligatoria'
                    }), 400
                
                # ===== VALIDAR STOCK MÍNIMO =====
                if 'stock_minimo' in data:
                    stock_minimo = data.get('stock_minimo')
                    
                    if stock_minimo is not None:
                        if not isinstance(stock_minimo, int) or stock_minimo < 0:
                            return jsonify({
                                'error': 'Stock mínimo inválido',
                                'detail': 'El stock_minimo debe ser un entero >= 0'
                            }), 400
                        
                        # Validar rango razonable
                        if stock_minimo > 1000000:
                            return jsonify({
                                'error': 'Stock mínimo inválido',
                                'detail': 'El stock_minimo excede el valor máximo permitido'
                            }), 400
                
                # ===== VALIDAR UNIDAD DE MEDIDA =====
                if 'unidad_medida' in data:
                    unidad_medida = data.get('unidad_medida')
                    
                    if unidad_medida is not None:
                        if not isinstance(unidad_medida, str):
                            return jsonify({
                                'error': 'Unidad de medida inválida',
                                'detail': 'La unidad_medida debe ser un string'
                            }), 400
                        
                        unidad_medida = unidad_medida.strip().lower()
                        
                        # Lista de unidades válidas
                        unidades_validas = [
                            'kg', 'g', 'mg', 'l', 'ml', 'unidad', 'unidades',
                            'caja', 'cajas', 'paquete', 'paquetes', 'bolsa', 'bolsas',
                            'm', 'cm', 'mm', 'm2', 'm3', 'docena'
                        ]
                        
                        if unidad_medida not in unidades_validas:
                            return jsonify({
                                'error': 'Unidad de medida inválida',
                                'detail': f'Unidades válidas: {", ".join(unidades_validas)}'
                            }), 400
                        
                        data['unidad_medida'] = unidad_medida
                
                # ===== VALIDAR CÓDIGO DE BARRAS =====
                if 'codigo_barras' in data:
                    codigo_barras = data.get('codigo_barras')
                    
                    if codigo_barras is not None:
                        if not isinstance(codigo_barras, str):
                            return jsonify({
                                'error': 'Código de barras inválido',
                                'detail': 'El codigo_barras debe ser un string'
                            }), 400
                        
                        codigo_barras = codigo_barras.strip()
                        
                        # Solo dígitos, longitud entre 8-18 caracteres (EAN-8, EAN-13, etc)
                        if not re.match(r'^\d{8,18}$', codigo_barras):
                            return jsonify({
                                'error': 'Código de barras inválido',
                                'detail': 'El código de barras debe contener solo dígitos (8-18 caracteres)'
                            }), 400
                        
                        data['codigo_barras'] = codigo_barras
                
                # ===== VALIDAR ACTIVO (BOOLEAN) =====
                if 'activo' in data:
                    activo = data.get('activo')
                    
                    if not isinstance(activo, bool):
                        return jsonify({
                            'error': 'Estado inválido',
                            'detail': 'El campo activo debe ser true o false'
                        }), 400
                
                # Si pasa todas las validaciones, ejecutar la función
                return fn(*args, **kwargs)
                
            except Exception as e:
                return jsonify({
                    'error': 'Error al validar datos',
                    'detail': str(e)
                }), 500
        
        return wrapper
    return decorator


def _tiene_patron_sql_injection(texto: str) -> bool:
    """
    Detecta patrones comunes de SQL injection
    
    Args:
        texto: String a validar
    
    Returns:
        bool: True si detecta patrones sospechosos
    """
    # Convertir a minúsculas para comparación
    texto_lower = texto.lower()
    
    # Patrones de SQL injection
    patrones_peligrosos = [
        r"('|(\\')|(;)|(--)|(/\*))",  # Comillas, punto y coma, comentarios
        r"(\bunion\b.*\bselect\b)",   # UNION SELECT
        r"(\bdrop\b.*\b(table|database)\b)",  # DROP TABLE/DATABASE
        r"(\binsert\b.*\binto\b)",    # INSERT INTO
        r"(\bupdate\b.*\bset\b)",     # UPDATE SET
        r"(\bdelete\b.*\bfrom\b)",    # DELETE FROM
        r"(\bexec\b.*\()",            # EXEC(
        r"(\bscript\b.*>)",           # <script> tag
        r"(\bor\b.*=.*)",             # OR 1=1
        r"(\band\b.*=.*)",            # AND 1=1
        r"xp_cmdshell",               # SQL Server command execution
        r"(\bselect\b.*\bfrom\b)",    # SELECT FROM
    ]
    
    for patron in patrones_peligrosos:
        if re.search(patron, texto_lower, re.IGNORECASE):
            return True
    
    return False


def sanitize_producto_string(value: str, max_length: int = 255) -> str:
    """
    Sanitiza strings de productos
    
    Args:
        value: String a sanitizar
        max_length: Longitud máxima
    
    Returns:
        String sanitizado
    """
    if not isinstance(value, str):
        raise ValueError("El valor debe ser un string")
    
    # Eliminar espacios al inicio y final
    value = value.strip()
    
    # Truncar si es muy largo
    value = value[:max_length]
    
    # Eliminar caracteres de control
    value = re.sub(r'[\x00-\x1F\x7F]', '', value)
    
    return value
