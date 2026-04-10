import pandas as pd
import pymysql
import os
import re
from dotenv import load_dotenv

# =========================
# CONFIG
# =========================

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'aguas_rionegrinas_db_explotacion'),
    'charset': 'utf8mb4'
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "Stock.xlsx")

ID_LOCALIDAD_DEFAULT = 1
ID_LUGAR_DEFAULT = 196

# =========================
# FUNCIONES
# =========================

# def separar_material(texto):
#     texto = str(texto).upper().strip()
    
#     if " DE " in texto:
#         nombre, descripcion = texto.split(" DE ", 1)
#     else:
#         partes = texto.split()
#         nombre = partes[0]
#         descripcion = " ".join(partes[1:])
    
#     return nombre.strip(), descripcion.strip()

def separar_material(texto):
    texto = str(texto).upper().strip()
    
    # Buscamos patrones de medidas comunes: Ø 50mm, 1/2, 110mm, etc.
    # Esta regex busca: (Simbolo Ø opcional) + Numero + (unidades mm, " o /)
    patron_medida = r'(Ø\s?\d+|(?:\d+/\d+["\']?)|(?:\d+MM))'
    
    match = re.search(patron_medida, texto)
    
    if match:
        # El nombre será todo lo que esté hasta la medida inclusive
        punto_corte = match.end()
        nombre = texto[:punto_corte].strip()
        descripcion = texto[punto_corte:].strip()
        
        # Limpieza de la descripción si quedó empezando con "DE"
        if descripcion.startswith("DE "):
            descripcion = descripcion[3:].strip()
            
    elif " DE " in texto:
        # Si no hay medidas pero hay un "DE", mantenemos tu lógica anterior
        nombre, descripcion = texto.split(" DE ", 1)
    else:
        # Caso base: separar por la primera palabra
        partes = texto.split()
        nombre = partes[0]
        descripcion = " ".join(partes[1:])
    
    return nombre.strip(), descripcion.strip()


def limpiar_texto(texto):
    if not texto:
        return ""
    texto = texto.strip()
    texto = re.sub(r'\s+', ' ', texto)
    return texto


def detectar_unidad(nombre, descripcion):
    texto = f"{nombre} {descripcion}".upper()
    
    if "CAÑO" in texto or "MANGUERA" in texto:
        return "metro"
    
    return "unidad"


def asignar_categoria(material):
    material = str(material).upper()
    
    # 1. ABRAZADERAS
    if "ABRAZADERA" in material:
        return 1
    
    # 2. CONEXIONES (Accesorios de unión en general)
    elif any(x in material for x in ["CONEXION", "ACOPLE", "ADAPTADOR", "BRIDA", "CUPLA", "NIPLE"]):
        return 2
    
    # 3. ESPIGAS
    elif "ESPIGA" in material:
        return 3
    
    # 4. ESTRIBOS
    elif "ESTRIBO" in material:
        return 4
    
    # 5. HIDRÁULICOS
    elif any(x in material for x in ["HIDRAULICO", "VALVULA", "COMANDO", "PISTON"]):
        return 5
    
    # 6. JUNTAMAS
    elif "JUNTAMA" in material: # Cubre Juntamas o Juntama
        return 6
    
    # 7. JUNTAS GIBAULT
    elif "GIBAULT" in material:
        return 7
    
    # 9. REDUCCIONES
    elif "REDUCCION" in material or "REDUCCION BUSHING" in material:
        return 9
    
    # 10. TUBERÍAS PVC (Prioridad sobre material genérico)
    elif any(x in material for x in ["CAÑO PVC", "TUBO PVC", "TUBERIA PVC"]):
        return 10
    
    # MATERIAL (Categoría genérica 4 - según tu imagen es para soportes/fijación o genérico)
    # Nota: En tu imagen la categoría 4 dice "Soportes metálicos", pero el script original 
    # la usaba para caños. Si es un caño común, podrías dejarlo en 4 o crear una nueva.
    elif any(x in material for x in ["CAÑO", "TUBO", "CURVA", "CODO"]):
        return 4 

    # 8. OTROS
    else:
        return 8


def generar_codigo(nombre, descripcion, index):
    base = (nombre[:3] + descripcion[:3]).upper()
    base = re.sub(r'[^A-Z0-9]', '', base)
    return f"{base}{index:04d}"


# =========================
# MAIN
# =========================

def main():
    print("\n📦 Iniciando proceso...\n")

    # =========================
    # LEER EXCEL
    # =========================

    materiales_data = pd.read_excel("Stock.xlsx", sheet_name="materiales", skiprows=4)

    stock_data = pd.read_excel("Stock.xlsx", sheet_name="Stock", skiprows=3)

    # =========================
    # LIMPIEZA
    # =========================

    data_unique = materiales_data.drop_duplicates(
        subset=[materiales_data.columns[1]]
    ).dropna(subset=[materiales_data.columns[1]])

    datos_stock = stock_data.drop_duplicates(
        subset=[stock_data.columns[1]]
    ).dropna(subset=[stock_data.columns[1]])

    # Normalizar strings
    data_unique.iloc[:,1] = data_unique.iloc[:,1].astype(str).str.strip()
    datos_stock.iloc[:,1] = datos_stock.iloc[:,1].astype(str).str.strip()

    # =========================
    # STOCK DICT (para asignar stock a cada material)
    # =========================

    stock_dict = {}
    for _, row in datos_stock.iterrows():
        if pd.notna(row.iloc[1]):
            nombre_material = str(row.iloc[1]).strip().upper()
            # Convertimos a numérico primero
            valor_stock = pd.to_numeric(row.iloc[2], errors='coerce')
            
            # Si el valor es NaN (vacío o error), le asignamos 0, sino el valor real
            # Luego lo convertimos a int con seguridad
            cantidad = int(valor_stock) if pd.notna(valor_stock) else 0
            
            stock_dict[nombre_material] = cantidad

    # =========================
    # CONEXIÓN BD
    # =========================

    connection = pymysql.connect(**DB_CONFIG)

    try:
        with connection.cursor() as cursor:

            insert_producto = """
                INSERT INTO productos 
                (nombre, codigo, descripcion, id_categoria, costo, unidad_medida, stock_minimo, activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
                ON DUPLICATE KEY UPDATE id_producto = LAST_INSERT_ID(id_producto)
            """

            insert_stock = """
                INSERT INTO productos_localidad 
                (id_producto, id_localidad, id_lugar, cantidad)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE cantidad = %s
            """

            # =========================
            # PROCESAMIENTO
            # =========================

            for index, row in data_unique.iterrows():
                try:
                    codigo = row.iloc[0]
                    material = row.iloc[1]

                    # Separar
                    nombre, descripcion = separar_material(material)

                    # Limpiar
                    nombre = limpiar_texto(nombre)
                    descripcion = limpiar_texto(descripcion)

                    # Unidad
                    unidad = detectar_unidad(nombre, descripcion)

                    # Categoría
                    id_categoria = asignar_categoria(material)

                    # Código
                    if pd.isna(codigo) or not codigo:
                        codigo = generar_codigo(nombre, descripcion, index)

                    # Stock
                    cantidad = stock_dict.get(material, 0)

                    # INSERT PRODUCTO
                    cursor.execute(insert_producto, (
                        nombre,
                        codigo,
                        descripcion,
                        id_categoria,
                        0,
                        unidad,
                        1
                    ))

                    id_producto = cursor.lastrowid

                    # INSERT STOCK
                    cursor.execute(insert_stock, (
                        id_producto,
                        ID_LOCALIDAD_DEFAULT,
                        ID_LUGAR_DEFAULT,
                        cantidad,
                        cantidad
                    ))  

                    print(f"✅ {nombre} → stock: {cantidad}")

                except Exception as e:
                    print(f"❌ Error fila {index}: {e}")

        connection.commit()
        print("\n🎉 Migración completada")

    except Exception as e:
        print(f"❌ Error general: {e}")
        connection.rollback()

    finally:
        connection.close()


# =========================
# RUN
# =========================

if __name__ == "__main__":
    main()