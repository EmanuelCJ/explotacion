import pandas as pd

# 1. Leer la hoja materiales desde fila 5 (skiprows=4)
data = pd.read_excel("data/Stock.xlsx", sheet_name="materiales", skiprows=4)

materiales_list = []

data_unique = data.drop_duplicates(subset=[data.columns[1]]).dropna(subset=[data.columns[1]])

 # 3. Función para asignar categorías
def asignar_categoria(material):
    material = str(material).upper()
    if "ABRAZADERA" in material:
        return "Abrazaderas"
    elif "ACOPLE" in material or "ADAPTADOR" in material or "BRIDA" in material:
        return "Conexiones"
    elif "HIDRANTE" in material or "CABEZAL" in material:
        return "Hidráulicos"
    elif "CAÑO" in material or "CODOS" in material or "CUPLA" in material or "CURVA" in material:
        return "Tuberías PVC"
    elif "ESPIGA" in material:
        return "Espigas"
    elif "JUNTA GIBAULT" in material:
        return "Juntas Gibault"
    elif "SILLA ESTRIBO" in material:
        return "Estribos"
    elif "JUNTAMAS" in material:
        return "Juntamas"
    elif "TRANSICIÓN" in material:
        return "Transiciones"
    elif "REDUCCIÓN" in material:
        return "Reducciones"
    else:
        return "Otros"

for index, row in data_unique.iterrows():
    # Asegurarse de procesar todas las filas
        if pd.notna(row.iloc[1]): #verificar que la columna MATERIAL no esté vacía
            codigo = row.iloc[0]
            material = row.iloc[1]
            categoria = asignar_categoria(material)
            materiales_list.append({
                "codigo": codigo, 
                "material": material, 
                "categoria": categoria
            })
        
print(f"Se procesaron {len(materiales_list)} materiales únicos.")


# 4. Crear un DataFrame con los materiales categorizados
materiales_categorizados = pd.DataFrame(materiales_list)


# 5. Guardar el DataFrame en un nuevo archivo CSV
materiales_categorizados.to_csv("data/materiales_categorizados.csv", index=False, encoding="utf-8-sig")
print("Archivo 'materiales_categorizados.csv' creado correctamente.")