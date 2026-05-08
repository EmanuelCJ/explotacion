FROM python:3.11-slim

WORKDIR /app

# Instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el contenido de BACKEND al contenedor
COPY . .

# Ejecutamos con run.py que parece ser tu punto de entrada
CMD ["python", "run.py"]