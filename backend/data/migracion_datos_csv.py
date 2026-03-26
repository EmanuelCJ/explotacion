# from app.db.conexion_DB import ConectDB
import pandas as pd
import re

info = pd.read_csv('data/materiales_categorizados.csv')


def asignar_unidad(categoria):
    categoria = str(categoria).upper()

    if "Tuberias PVC" in categoria:
        return "Metros"
    else:
        return "Unidades"

for index, row in info.iterrows():
    id_material = row.iloc[0]
    nombre = row.iloc[1]
    categoria = row.iloc[2]
    unidad_medida = asignar_unidad(categoria)
    
    print(f"ID: {id_material}, Nombre: {nombre}, Categoría: {categoria}, Unidad de Medida: {unidad_medida}")