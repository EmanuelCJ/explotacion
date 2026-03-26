# from app.db.conexion_DB import ConectDB
import pandas as pd

info = pd.read_csv('data/materiales_categorizados.csv')


for index, row in info.iterrows():
    id_material = row.iloc[0]
    nombre = row.iloc[1]
    categoria = row.iloc[2]

    
    
    print(f"ID: {id_material}, Nombre: {nombre}, Categoria: {categoria}")