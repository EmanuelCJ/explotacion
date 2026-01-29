#nos permite conectarnos a la base de datos MySQL
from mysql.connector import connect, Error
#nos permite cargar variables de entorno desde un archivo .env
import os
#cargar las variables de entorno desde el archivo .env
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class ConectDB():
    @staticmethod
    def get_connection():
        try:
            connection = connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            return connection
        except Error as e:
            print(f"Error connecting to the database: {e}")
            return None
