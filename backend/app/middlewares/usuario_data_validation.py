# usuario_data_validation.py

import re
from functools import wraps
from flask import request, jsonify

# =========================
# EXPRESIONES REGULARES
# =========================

EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'

# Detecta patrones típicos de SQL Injection
SQL_INJECTION_REGEX = re.compile(
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|EXEC|OR|AND)\b|--|;|'|\"|\*)",
    re.IGNORECASE
)


# =========================
# FUNCIONES AUXILIARES
# =========================

def contiene_sql_injection(valor):
    """
    Verifica si un string contiene patrones peligrosos.
    """

    if not isinstance(valor, str):
        return False

    return bool(SQL_INJECTION_REGEX.search(valor))


def validar_texto(campo, valor, min_len=2, max_len=50):
    """
    Validación genérica para textos.
    """

    if not isinstance(valor, str):
        return f"El campo '{campo}' debe ser texto"

    valor = valor.strip()

    if len(valor) < min_len:
        return f"El campo '{campo}' debe tener al menos {min_len} caracteres"

    if len(valor) > max_len:
        return f"El campo '{campo}' no puede superar {max_len} caracteres"

    if contiene_sql_injection(valor):
        return f"El campo '{campo}' contiene caracteres inválidos"

    return None


# =========================
# DECORADOR
# =========================

def usuario_data_validation(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No se enviaron datos JSON"
            }), 400

        campos_obligatorios = [
            "nombre",
            "apellido",
            "username",
            "email",
            "password",
            "legajo",
            "id_localidad",
            "id_rol"
        ]

        # =========================
        # VALIDAR CAMPOS FALTANTES
        # =========================

        for campo in campos_obligatorios:
            if campo not in data:
                return jsonify({
                    "error": f"Falta el campo '{campo}'"
                }), 400

        # =========================
        # VALIDAR TEXTOS
        # =========================

        campos_texto = [
            "nombre",
            "apellido",
            "username",
            "password"
        ]

        for campo in campos_texto:

            error = validar_texto(campo, data[campo])

            if error:
                return jsonify({
                    "error": error
                }), 400

        # =========================
        # VALIDAR EMAIL
        # =========================

        email = data["email"]

        if not isinstance(email, str):
            return jsonify({
                "error": "El email debe ser texto"
            }), 400

        email = email.strip()

        if not re.match(EMAIL_REGEX, email):
            return jsonify({
                "error": "Formato de email inválido"
            }), 400

        if contiene_sql_injection(email):
            return jsonify({
                "error": "Email inválido"
            }), 400

        # =========================
        # VALIDAR IDS
        # =========================

        campos_enteros = [
            "id_localidad",
            "id_rol",
            "legajo"
        ]

        for campo in campos_enteros:

            if not isinstance(data[campo], int):
                return jsonify({
                    "error": f"El campo '{campo}' debe ser entero"
                }), 400

            if data[campo] <= 0:
                return jsonify({
                    "error": f"El campo '{campo}' debe ser mayor a 0"
                }), 400

        # =========================
        # DATOS LIMPIOS
        # =========================

        request.usuario_validado = {
            "nombre": data["nombre"].strip(),
            "apellido": data["apellido"].strip(),
            "username": data["username"].strip(),
            "email": email,
            "password": data["password"].strip(),
            "legajo": data["legajo"].strip(),
            "id_localidad": data["id_localidad"],
            "id_rol": data["id_rol"]
        }

        return f(*args, **kwargs)

    return decorated_function