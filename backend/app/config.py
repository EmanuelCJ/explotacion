import os
from datetime import timedelta


def str_to_bool(value: str) -> bool:
    return str(value).lower() in ("true", "1", "yes")


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY")
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = str_to_bool(os.getenv("FLASK_DEBUG", "False"))

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    JWT_TOKEN_LOCATION = ["cookies"]

    JWT_ACCESS_COOKIE_NAME = os.getenv("JWT_ACCESS_COOKIE_NAME", "access_token")
    JWT_REFRESH_COOKIE_NAME = os.getenv("JWT_REFRESH_COOKIE_NAME", "refresh_token")

    JWT_COOKIE_SECURE = str_to_bool(os.getenv("JWT_COOKIE_SECURE", "False"))
    JWT_COOKIE_HTTPONLY = str_to_bool(os.getenv("JWT_COOKIE_HTTPONLY", "True"))
    JWT_COOKIE_CSRF_PROTECT = str_to_bool(os.getenv("JWT_COOKIE_CSRF_PROTECT", "False"))

    
    JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")

    # Expiración de tokens
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 60))
    )

    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 15))
    )

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")

    # Database
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")