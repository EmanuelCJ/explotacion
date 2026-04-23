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

productos = [
    {
        "nombre": "Filtro de agua doméstico",
        "codigo": "HIDFIL1234",
        "descripcion": "Filtro para purificación de agua en hogares",
        "id_categoria": 1,
        "costo": 2500.50,
        "unidad_medida": "unidad",
        "stock_minimo": 10
    },
    {
        "nombre": "Tanque de almacenamiento 500L",
        "codigo": "HIDTAN5678",
        "descripcion": "Tanque plástico para almacenamiento de agua potable",
        "id_categoria": 2,
        "costo": 12000.00,
        "unidad_medida": "litros",
        "stock_minimo": 5
    },
    {
        "nombre": "Bomba sumergible",
        "codigo": "HIDBOM4321",
        "descripcion": "Bomba eléctrica para extracción de agua subterránea",
        "id_categoria": 3,
        "costo": 8500.75,
        "unidad_medida": "unidad",
        "stock_minimo": 3
    },
    {
        "nombre": "Manguera reforzada 20m",
        "codigo": "HIDMAN8765",
        "descripcion": "Manguera flexible para riego y conducción de agua",
        "id_categoria": 4,
        "costo": 3200.00,
        "unidad_medida": "metro",
        "stock_minimo": 15
    },
    {
        "nombre": "Purificador portátil",
        "codigo": "HIDPUR1357",
        "descripcion": "Dispositivo portátil para potabilizar agua en viajes",
        "id_categoria": 5,
        "costo": 1800.00,
        "unidad_medida": "unidad",
        "stock_minimo": 8
    },
    {
        "nombre": "Bidón de agua 20L",
        "codigo": "HIDBID2468",
        "descripcion": "Bidón plástico reutilizable para transporte de agua",
        "id_categoria": 6,
        "costo": 600.00,
        "unidad_medida": "litros",
        "stock_minimo": 20
    },
    {
        "nombre": "Regador manual",
        "codigo": "HIDREG9753",
        "descripcion": "Regador de mano para jardinería",
        "id_categoria": 7,
        "costo": 450.00,
        "unidad_medida": "unidad",
        "stock_minimo": 12
    },
    {
        "nombre": "Canilla metálica",
        "codigo": "HIDCAN8642",
        "descripcion": "Grifo metálico para instalaciones de agua",
        "id_categoria": 8,
        "costo": 750.00,
        "unidad_medida": "unidad",
        "stock_minimo": 25
    },
    {
        "nombre": "Kit de riego por goteo",
        "codigo": "HIDKIT7531",
        "descripcion": "Sistema completo de riego eficiente para huertas",
        "id_categoria": 9,
        "costo": 5400.00,
        "unidad_medida": "unidad",
        "stock_minimo": 6
    },
    {
        "nombre": "Medidor de caudal",
        "codigo": "HIDMED1597",
        "descripcion": "Instrumento para medir el flujo de agua",
        "id_categoria": 10,
        "costo": 2200.00,
        "unidad_medida": "unidad",
        "stock_minimo": 4
    }
]

def main():
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

            for producto in productos:
                try:

                    # INSERT PRODUCTO
                    cursor.execute(insert_producto, (
                        producto["nombre"],
                        producto["codigo"],
                        producto["descripcion"],
                        producto["id_categoria"],
                        producto["costo"],
                        producto["unidad_medida"],
                        producto["stock_minimo"]
                    ))

                    id_producto = cursor.lastrowid

                    # INSERT STOCK
                    cursor.execute(insert_stock, (
                        id_producto,
                        ID_LOCALIDAD_DEFAULT,
                        ID_LUGAR_DEFAULT,
                        producto["stock_minimo"],
                        producto["stock_minimo"]
                    ))  

                    print(f"✅ {producto['nombre']} → stock: {producto['stock_minimo']  }")

                except Exception as e:
                    print(f"❌ Error fila {producto['nombre']}: {e}")

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