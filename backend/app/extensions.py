
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import get_jwt_identity
import os
#cargar las variables de entorno desde el archivo .env
from dotenv import load_dotenv

#
dia = os.getenv("DIA")
hora = os.getenv("HORA")
minuto = os.getenv("MINUTOS")


def limiter_key():
    try:
        user_id = get_jwt_identity()
        if user_id:
            return f"user:{user_id}"
    except:
        pass

    return get_remote_address()

jwt = JWTManager()
cors = CORS()

# #Limitador de peticiones
limiter = Limiter(
    key_func=limiter_key,
    default_limits=[dia, hora]
)
            
