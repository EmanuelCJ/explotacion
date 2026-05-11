FROM python:3.11-slim

WORKDIR /app

# Instalamos dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiamos todo el contenido de BACKEND al contenedor
COPY . .

EXPOSE 5000

# Ejecutamos con run.py que parece ser tu punto de entrada
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
