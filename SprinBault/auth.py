from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import RedirectResponse
import jwt
from datetime import datetime, timedelta
import os

load_dotenv()

# Función para obtener el TOKEN_VALUE desencriptado desde la base de datos
def get_token_value():
    token_value = os.getenv("TOKEN_VALUE")
    if not token_value:
        raise Exception("No se pudo obtener el TOKEN_VALUE del archivo .env.")
    return token_value

# Función para crear el JWT (usando el TOKEN_VALUE desencriptado)
def create_access_token(data: dict, expires_delta: timedelta = None):
    token_value = get_token_value()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=10)
    to_encode.update({"exp": expire})  # Añadir expiración al payload

    encoded_jwt = jwt.encode(to_encode, token_value, algorithm="HS256")
    return encoded_jwt

# Función para verificar el token de acceso
def verify_token(token: str, request: Request):
    try:
        token_value = get_token_value()
        payload = jwt.decode(token, token_value, algorithms=["HS256"])

        # Refrescar token si faltan menos de 30 segundos
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            remaining = datetime.utcfromtimestamp(exp_timestamp) - datetime.utcnow()
            if remaining < timedelta(seconds=30):
                refreshed_token = create_access_token(
                    {"sub": payload["sub"], "is_admin": payload["is_admin"]},
                    expires_delta=timedelta(minutes=10)
                )
                response = RedirectResponse(url=request.url.path, status_code=303)
                response.set_cookie(
                    key="access_token", value=refreshed_token, httponly=True, samesite="Lax", path="/"
                )
                return response  # Devuelve una redirección con el token renovado

        return payload

    except jwt.ExpiredSignatureError:
        response = RedirectResponse(url="/?error=token_expired", status_code=303)
        response.delete_cookie("access_token")
        response.delete_cookie("is_admin")
        response.delete_cookie("email")
        response.delete_cookie("refresh_token")
        return response
    except jwt.InvalidTokenError:
        response = RedirectResponse(url="/?error=token_not_found", status_code=303)
        return response