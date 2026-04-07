# from app.db.conexion_DB import ConectDB

"""
Script de inicialización de base de datos
Sistema de Inventario - Aguas Rionegrinas
Río Negro, Argentina
"""

import pymysql
import bcrypt
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd
import re

# Cargar variables de entorno
load_dotenv()

# leemos el csv
info = pd.read_csv('data/materiales_categorizados.csv')

# Configuración de base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'charset': 'utf8mb4'
}

DB_NAME = os.getenv('DB_NAME', 'aguas_rionegrinas_db_explotacion')


def init_migracion():
    
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS {DB_NAME} 
                CHARACTER SET utf8mb4 
                COLLATE utf8mb4_unicode_ci
            """)
            print(f"✅ Base de datos '{DB_NAME}' creada/verificada")
    finally:
        connection.close()



def asignar_unidad(categoria: str) -> str:
    categoria = str(categoria).upper()

    if "Tuberias PVC" in categoria:
        return "Metros"
    else:
        return "Unidades"

def ejecutar_migracion():
    for index, row in info.iterrows():
        id_material = row.iloc[0]
        nombre = row.iloc[1]
        categoria = row.iloc[2]
        unidad_medida = asignar_unidad(categoria)
        
        print(f"ID: {id_material}, Nombre: {nombre}, Categoría: {categoria}, Unidad de Medida: {unidad_medida}")


"""

{
    "nombre": "ADAPTADOR",
    "descripcion": "BRIDADO Ø8” ",
    "id_categoria": 8,
    "costo": 30000,
    "unidad_medida": "unidad",
    "stock_minimo": 1,
    "id_lugar": 1
}


"""

