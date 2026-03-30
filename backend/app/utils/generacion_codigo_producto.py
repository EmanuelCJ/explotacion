# Este archivo contiene una funcion que crea un codigo de producto unico en base a la informacion del producto, se utiliza al crear un nuevo producto para generar un codigo

@staticmethod
def generar_codigo_producto(nombre: str, categoria: str) -> str:
    """
    Generar un código de producto único basado en el nombre y categoría
    
    Args:
        nombre (str): Nombre del producto
        categoria (str): Nombre de la categoría
    
    Returns:
        str: Código de producto generado
    """
    # Limpiar y formatear el nombre y categoría
    nombre_limpio = ''.join(e for e in nombre if e.isalnum()).upper()
    categoria_limpia = ''.join(e for e in categoria if e.isalnum()).upper()
    
    # Tomar las primeras 3 letras del nombre y categoría
    parte_nombre = nombre_limpio[:3] if len(nombre_limpio) >= 3 else nombre_limpio.ljust(3, 'X')
    parte_categoria = categoria_limpia[:3] if len(categoria_limpia) >= 3 else categoria_limpia.ljust(3, 'X')
    
    # Generar un número aleatorio de 4 dígitos
    import random
    numero_aleatorio = random.randint(1000, 9999)
    
    # Combinar para formar el código
    codigo_producto = f"{parte_categoria}{parte_nombre}{numero_aleatorio}"
    
    return codigo_producto