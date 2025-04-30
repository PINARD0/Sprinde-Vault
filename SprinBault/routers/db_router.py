from datetime import timedelta
from fastapi import APIRouter, Depends, Request, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import jwt
import pymysql
from database import get_connection_monedero, get_connection_sprinde
from auth import create_access_token, get_token_value, verify_token
from security import decrypt_with_master, encrypt_with_master, hash_password, verify_password
from pydantic import BaseModel, EmailStr
from routers.db_queries import get_all_users, get_all_hardware, get_email_by_email, get_email_password, get_hardware_types, get_hardware_types, get_location_codes, insert_email, insert_hardware, get_hardware_password, get_user_by_email, insert_location_code, insert_user, delete_user_by_id, insert_hardware_types

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

class MasterPasswordRequest(BaseModel):
    password: str
    hardware_id: int

# Endpoint para mostrar la página de login
@router.get("/")
async def login_page(request: Request):
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/dashboard")  # Redirigir si ya tiene sesión activa
    return templates.TemplateResponse("form.html", {"request": request})


# Endpoint para procesar el login y generar el JWT
@router.post("/login")
async def login(
    email: EmailStr = Form(...), password: str = Form(...)
):
    user = get_user_by_email(email)
    
    if user and verify_password(password, user["password_hash"]):
        # Crear el access token con expiración corta
        access_token_expires = timedelta(minutes=10)
        access_token = create_access_token(
            data={"sub": email, "is_admin": user["is_admin"]},
            expires_delta=access_token_expires
        )

        # Crear el refresh token con expiración más larga
        refresh_token_expires = timedelta(days=1)  # Este tiene más duración
        refresh_token = create_access_token(
            data={"sub": email, "is_admin": user["is_admin"]},
            expires_delta=refresh_token_expires
        )

        # Crear la respuesta de redirección a /dashboard si las credenciales son válidas
        response = RedirectResponse(url="/dashboard", status_code=303)

        # Eliminar cualquier cookie previa
        response.delete_cookie("access_token")
        response.delete_cookie("is_admin")
        response.delete_cookie("email")
        response.delete_cookie("refresh_token") 

        # Guardar el nuevo access token en la cookie
        response.set_cookie(
            key="access_token", value=access_token, httponly=True, samesite="Lax", path="/"
        )

        # Guardar el refresh token en la cookie
        response.set_cookie(
            key="refresh_token", value=refresh_token, httponly=True, samesite="Lax", path="/"
        )

        # Guardar is_admin en una cookie accesible desde JavaScript
        response.set_cookie(
            key="is_admin", value=str(user["is_admin"]), httponly=False, samesite="Lax", path="/"
        )

        # Guardar email en una cookie accesible desde JavaScript
        response.set_cookie(
            key="email", value=email, httponly=False, samesite="Lax", path="/"
        )

        return response
    else:
        return RedirectResponse(url="/?error=invalid_credentials", status_code=303)


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    
    response.delete_cookie("access_token")
    response.delete_cookie("is_admin")
    response.delete_cookie("email")
    response.delete_cookie("refresh_token")
    
    return response


@router.get("/get-role")
async def get_role(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    payload = verify_token(token, request)
    return {"is_admin": payload.get("is_admin")}


# Endpoint para registrarse
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# Endpoint para procesar el registro
@router.post("/register")
async def register_user(
    request: Request, email: EmailStr = Form(...), 
    password: str = Form(...), confirm_password: str = Form(...)
):
    # Comprobar si las contraseñas coinciden
    if password != confirm_password:
        return RedirectResponse(url="/register?error=password_mismatch", status_code=303)

    hashed_password = hash_password(password)

    try:
        # Verificar si el correo ya está registrado
        with get_connection_sprinde() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                if cursor.fetchone():  # Si el correo ya existe
                    return RedirectResponse(url="/register?error=email_exists", status_code=303)

        # Insertar usuario
        insert_user(email, hashed_password)
        return RedirectResponse(url="/users", status_code=303)

    except Exception as e:
        return {"error": str(e)}


# Función para obtener el token desde las cookies
def get_token_from_cookies(request: Request):
    token = request.cookies.get("access_token")
    if token is None:
        # Redirigir al formulario de login con el mensaje de token no encontrado
        return RedirectResponse(url="/?error=token_not_found", status_code=303)
    return token


@router.post("/refresh-token")
async def refresh_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return JSONResponse(content={"status": "no_token"})

    try:
        token_value = get_token_value()
        payload = jwt.decode(token, token_value, algorithms=["HS256"], options={"verify_exp": False})
        new_token = create_access_token(
            {"sub": payload["sub"], "is_admin": payload["is_admin"]},
            expires_delta=timedelta(minutes=10)
        )
        response = JSONResponse(content={"status": "refreshed"})
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            samesite="Lax",
            path="/"
        )
        return response
    except Exception:
        return JSONResponse(content={"status": "error"})


# Endpoint para mostrar el dashboard
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, token: str = Depends(get_token_from_cookies)):
    if isinstance(token, RedirectResponse):
        return token

    payload = verify_token(token, request)
    if isinstance(payload, RedirectResponse):
        return payload  # ← si se renovó, el usuario será redirigido automáticamente

    email = payload.get("sub")
    is_admin = payload.get("is_admin")

    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "email": email, "is_admin": is_admin}
    )


# Endpoint para mostrar la página de usuarios con datos en tabla
@router.get("/users")
async def fetch_users(request: Request):
    users = get_all_users()
    
    # Obtener la cookie is_admin de la sesión
    is_admin = request.cookies.get("is_admin") == "1"
    
    return templates.TemplateResponse("users.html", {"request": request, "users": users, "is_admin": is_admin})


# Modelo para recibir JSON
class PasswordInput(BaseModel):
    password: str

# Endpoint para verificar la contraseña maestra para eliminar USUARIOS
@router.post("/verify-master-password-bbdd")
async def verify_master_password(data: PasswordInput):
    try:
        with get_connection_monedero() as db:
            with db.cursor() as cursor:
                cursor.execute("SELECT ciphertext FROM master_check WHERE id = 1")
                row = cursor.fetchone()
                if not row:
                    return JSONResponse(content={"valid": False}, status_code=400)
                ciphertext = row["ciphertext"]

        try:
            decrypted = decrypt_with_master(ciphertext, data.password)
            if decrypted == "TEST MASTER KEY":
                return {"valid": True}
        except Exception:
            pass

        return {"valid": False}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"valid": False, "error": str(e)}, status_code=500)


# Endpoint para eliminar un usuario por su ID
@router.post("/delete_user/{user_id}")
async def delete_user(request: Request, user_id: int):
    email = request.cookies.get("email")

    if not email:
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requiere autenticación.")

    success = delete_user_by_id(user_id)
    
    if success:
        response = RedirectResponse(url="/users", status_code=303)
        response.set_cookie(key="message", value="Usuario eliminado correctamente", max_age=5)
        return response
    else:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")


# Endpoint para eliminar hardware por ID
@router.post("/delete_hardware_type/{type_id}")
async def delete_hardware_type(request: Request, type_id: int):
    """Elimina un tipo de hardware por su ID y redirige a /hardware_types"""
    
    # Verificar si el usuario está autenticado
    email = request.cookies.get("email")

    if not email:
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requiere autenticación.")
    
    try:
        # Eliminar el tipo de hardware
        with get_connection_monedero() as connection:
            with connection.cursor() as cursor:
                query = "DELETE FROM hardwaretypes WHERE type_id = %s"
                cursor.execute(query, (type_id,))
                connection.commit()
                
        # Redirigir a la página de tipos de hardware después de eliminar
        return RedirectResponse(url="/hardware_types", status_code=303)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el tipo de hardware: {str(e)}")


# Endpoint para mostrar la página de cambiar contraseñas
@router.get("/modify_passwords", response_class=HTMLResponse)
async def modify_passwords_page(request: Request):
    # Obtener el usuario logueado desde la cookie
    email = request.cookies.get("email")
    error_message = request.query_params.get("error")
    success_message = request.query_params.get("success")

    if not email:
        return {"error": "No estás autenticado"}

    return templates.TemplateResponse("modify_passwords.html", {
        "request": request,
        "email": email,
        "error_message": error_message,
        "success_message": success_message
    })


# Endpoint para modificar contraseñas
@router.post("/modify_passwords")
async def create_password(
    request: Request, 
    password: str = Form(...), 
    confirm_password: str = Form(...)
):
    """Crea una nueva contraseña para el usuario logueado"""

    # Verificar que las contraseñas coincidan
    if password != confirm_password:
        return RedirectResponse(url="/modify_passwords?error=password_mismatch", status_code=303)

    # Obtener el usuario logueado desde la cookie
    email = request.cookies.get("email")
    if not email:
        return {"error": "No estás autenticado"}

    # Cifrar la contraseña antes de guardarla
    from security import hash_password  # Asegúrate de importar la función
    hashed_password = hash_password(password)

    # Guardar en la base de datos
    from routers.db_queries import save_password_for_user
    save_password_for_user(email, hashed_password)

    return RedirectResponse(url="/modify_passwords?success=password_changed", status_code=303)


# Endpoint para eliminar hardware
@router.post("/delete_hardware")
def delete_hardware(delete_hardware_id: int = Form(...)):
    with get_connection_monedero() as connection:
        try:
            with connection.cursor() as cursor:
                # Query para eliminar todo el hardware por su ID
                query = "DELETE FROM hardware WHERE id = %s"
                cursor.execute(query, (delete_hardware_id,))
                connection.commit()
            return {"message": "Hardware y contraseña eliminados correctamente"}
        except Exception as e:
            connection.rollback()
            return {"error": str(e)}


# Endpoint para actualizar contraseñas de hardware
@router.post("/manage_passwords")
async def update_hardware_password(
    hardware_id: int = Form(...),
    new_password: str = Form(...),
    confirm_new_password: str = Form(...),
    master_password: str = Form(...)
):
    if new_password != confirm_new_password:
        return JSONResponse(content={"error": "Las contraseñas no coinciden"}, status_code=400)

    # Verificación de contraseña maestra igual que en otros endpoints
    try:
        with get_connection_monedero() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT ciphertext FROM master_check WHERE id=1")
                row = cursor.fetchone()
                if not row:
                    return JSONResponse(content={"error": "Texto de verificación no encontrado."}, status_code=404)

                test_plain = decrypt_with_master(row["ciphertext"], master_password)
                if test_plain != "TEST MASTER KEY":
                    return JSONResponse(content={"error": "Contraseña maestra incorrecta"}, status_code=401)

    except Exception as e:
        print(f"❌ Error al verificar la contraseña maestra: {e}")
        return JSONResponse(content={"error": "Contraseña maestra incorrecta"}, status_code=401)

    # Si pasó la verificación, actualizamos la contraseña
    try:
        encrypted_password = encrypt_with_master(new_password, master_password)

        query = "UPDATE hardware SET password_hash = %s WHERE id = %s"
        with get_connection_monedero() as db:
            with db.cursor() as cursor:
                cursor.execute(query, (encrypted_password, hardware_id))
            db.commit()

        return JSONResponse(content={"message": "Contraseña actualizada correctamente"}, status_code=200)

    except Exception as e:
        print(f"❌ Error al actualizar contraseña: {e}")
        return JSONResponse(content={"error": "Error interno al actualizar la contraseña"}, status_code=500)


# Endpoint para mostrar la página de hardware con datos en tabla
@router.get("/hardware")
async def fetch_hardware(request: Request):
    hardware = get_all_hardware()

    # Obtener los tipos de hardware
    with get_connection_monedero() as db:
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT DISTINCT type_id, type_name FROM hardwaretypes")
        hardware_types = cursor.fetchall()

    # Obtener las localizaciones de la tabla location_code
    with get_connection_monedero() as db:
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT DISTINCT name FROM location_code")
        locations = cursor.fetchall()

    # Obtener la cookie is_admin de la sesión
    is_admin = request.cookies.get("is_admin") == "1"
    
    return templates.TemplateResponse(
        "hardware.html",
        {
            "request": request,
            "hardware": hardware,
            "is_admin": is_admin,
            "hardware_types": hardware_types,  # Pasamos los tipos de hardware
            "locations": locations  # Pasamos las localizaciones al template
        }
    )


# Desactivar hardware según location_code
@router.post("/disable_hardware/{location_code}")
async def disable_hardware(location_code: str):
    with get_connection_monedero() as db:
        cursor = db.cursor()
        cursor.execute("UPDATE hardware SET is_active = 0 WHERE Localizacion = %s", (location_code,))
        db.commit()
    return {"message": f"Hardware con location_code {location_code} desactivado"}

# Activar hardware según location_code
@router.post("/enable_hardware/{location_code}")
async def enable_hardware(location_code: str):
    with get_connection_monedero() as db:
        cursor = db.cursor()
        cursor.execute("UPDATE hardware SET is_active = 1 WHERE Localizacion = %s", (location_code,))
        db.commit()
    return {"message": f"Hardware con location_code {location_code} activado"}


# Endpoint para servir la página de modificación de hardware
@router.get("/modify_hardware", response_class=HTMLResponse)
async def modify_hardware(request: Request):
    # Obtener la lista de hardware y tipos de hardware desde la base de datos
    hardware = get_all_hardware()  # Lista de hardware
    hardware_types = get_hardware_types()  # Lista de tipos de hardware
    
    # Obtener la cookie is_admin de la sesión
    is_admin = request.cookies.get("is_admin") == "1"
    
    # Renderizar el template con la lista de hardware y tipos de hardware
    return templates.TemplateResponse("modify_hardware.html", {
        "request": request, 
        "hardware": hardware, 
        "hardware_types": hardware_types,
        "is_admin": is_admin
    })

# Endpoint para modificar hardware
@router.post("/update_hardware")
async def update_hardware(
    hardware_id: int = Form(...),
    new_ip: str = Form(None),
    new_name: str = Form(None),
    new_hardware_type: int = Form(None)
):
    # Actualizar la IP si se ha proporcionado
    if new_ip:
        query_ip = "UPDATE hardware SET IP = %s WHERE id = %s"
        with get_connection_monedero() as db:
            with db.cursor() as cursor:
                cursor.execute(query_ip, (new_ip, hardware_id))
            db.commit()

    # Actualizar el nombre si se ha proporcionado
    if new_name:
        query_name = "UPDATE hardware SET Nombre = %s WHERE id = %s"
        with get_connection_monedero() as db:
            with db.cursor() as cursor:
                cursor.execute(query_name, (new_name, hardware_id))
            db.commit()

    # Actualizar el tipo de hardware si se ha proporcionado
    if new_hardware_type:
        query_type = "UPDATE hardware SET Hardware_type_Id = %s WHERE id = %s"
        with get_connection_monedero() as db:
            with db.cursor() as cursor:
                cursor.execute(query_type, (new_hardware_type, hardware_id))
            db.commit()

    return JSONResponse(content={"message": "¡Hardware actualizado con éxito!"})


# Endpoint para mostrar la página de correos con datos en tabla
@router.get("/emails")
async def get_emails(request: Request):
    with get_connection_monedero() as db:
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM emails")
        emails = cursor.fetchall()
        
         # Obtener la cookie is_admin de la sesión
        is_admin = request.cookies.get("is_admin") == "1"

        # Obtener grupos únicos
        cursor.execute("SELECT DISTINCT grupo FROM emails")
        grupos = [row["grupo"] for row in cursor.fetchall()]

    return templates.TemplateResponse("emails.html", {"request": request, "emails": emails, "grupos": grupos, "is_admin": is_admin})


# Endpoint para verificar la contraseña maestra para hardware
@router.post("/verify-master-password")
async def verify_master_password(data: dict):
    """
    Cuando el usuario pide ver la contraseña de un hardware en concreto,
    éste envía su master_password y el ID del hardware.
    Con esa master_password derivamos la clave y desencriptamos.
    """
    master_password = data.get("password")
    hardware_id = data.get("hardware_id")

    # 1) Obtenemos de la BBDD la contraseña cifrada (no la clave)
    hardware_password_record = get_hardware_password(hardware_id)
    if not hardware_password_record:
        raise HTTPException(status_code=404, detail="Hardware no encontrado")

    encrypted_hardware_password = hardware_password_record['password_hash']

    # 2) Intentamos descifrar con la master_password real
    try:
        # Intentar descifrar la contraseña
        decrypted_password = decrypt_with_master(encrypted_hardware_password, master_password)
        
        # Si la contraseña descifrada es vacía, significa que la master password es incorrecta
        if not decrypted_password:
            raise HTTPException(status_code=401, detail="Contraseña maestra incorrecta")

    except Exception as e:
        # Si ocurre un error al intentar descifrar, lanzamos una excepción
        raise HTTPException(status_code=401, detail="Contraseña maestra incorrecta")

    # Si llegamos aquí, es porque la contraseña se descifró correctamente
    return {
        "message": "Contraseña maestra correcta",
        "hardware_password": decrypted_password
    }
    

# Endpoint para verficar la contraseña maestra para emails
@router.post("/verify-master-password-emails")
async def verify_email_password(data: dict):
    master_password = data.get("password")
    email_id = data.get("email_id")

    # Verificamos la master password con el texto fijo cifrado
    try:
        with get_connection_monedero() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT ciphertext FROM master_check WHERE id=1")
                row = cursor.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Texto de verificación no encontrado.")

                test_plain = decrypt_with_master(row["ciphertext"], master_password)
                if test_plain != "TEST MASTER KEY":
                    raise HTTPException(status_code=401, detail="Contraseña maestra incorrecta.")
    except Exception:
        raise HTTPException(status_code=401, detail="Contraseña maestra incorrecta.")

    # Si pasó la verificación, obtenemos la contraseña cifrada del email
    email_password = get_email_password(email_id)
    if not email_password:
        raise HTTPException(status_code=404, detail="Email no encontrado")

    decrypted_password = decrypt_with_master(email_password['password_hash'], master_password)

    return {
        "message": "Contraseña maestra correcta",
        "email_password": decrypted_password
    }


# Endpoint para mostrar la página de tipos de hardware con datos en tabla
@router.get("/hardware_types")
async def fetch_hardware_types(request: Request):
    hardware_types = get_hardware_types()
    
    # Obtener la cookie is_admin de la sesión
    is_admin = request.cookies.get("is_admin") == "1"
    
    return templates.TemplateResponse("hardware_types.html", {"request": request, "hardware_types": hardware_types, "is_admin": is_admin})


# Endpoint para mostrar la página de agregar tipos de hardware
@router.get("/insert_hardware_types", response_class=HTMLResponse)
async def add_hardware_type_page(request: Request):
    return templates.TemplateResponse("insert_hardware_types.html", {"request": request})


# Endpoint para insertar un nuevo tipo de hardware
@router.post("/insert_hardware_types")
async def add_hardware_type(type_name: str = Form(...)):
    with get_connection_monedero() as db:
        success = insert_hardware_types(db, type_name)

    if success:
        return RedirectResponse(url="/insert_hardware_types?success=true", status_code=303)
    else:
        return RedirectResponse(url="/insert_hardware_types?error=exists", status_code=303)
    

# Endpoint para mostrar la página de modificar tipos de hardware
@router.get("/modify_hardware_types")
async def modify_hardware_types(request: Request):
    # Obtener los tipos de hardware existentes desde la base de datos
    with get_connection_monedero() as db:
        cursor = db.cursor()
        cursor.execute("SELECT type_id, type_name FROM hardwaretypes")
        hardware_types = cursor.fetchall()

    # Pasar los tipos de hardware a la plantilla
    return templates.TemplateResponse("modify_hardware_types.html", {"request": request, "hardware_types": hardware_types})


# Endpoint para modificar un tipo de hardware
@router.post("/modify_hardware_type")
async def modify_hardware_type(existing_type: str = Form(...), new_type: str = Form(...)):
    try:
        with get_connection_monedero() as db:
            cursor = db.cursor()

            # Verificar si el nuevo tipo ya existe
            cursor.execute("SELECT type_id FROM hardwaretypes WHERE type_name = %s", (new_type,))
            existing_type_check = cursor.fetchone()

            if existing_type_check:
                # Si el tipo ya existe, retornar un error
                return {"success": False, "error": "El tipo de hardware ya existe."}
            
            # Si el tipo no existe, proceder con la actualización
            cursor.execute(
                "UPDATE hardwaretypes SET type_name = %s WHERE type_id = %s",
                (new_type, existing_type)
            )
            db.commit()

        # Respuesta de éxito
        return {"success": True}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


# Endpoint para eliminar un tipo de hardware
@router.post("/delete_hardware_type")
def delete_hardware_type(type_id: int = Form(...)):
    with get_connection_monedero() as connection:
        try:
            with connection.cursor() as cursor:
                # Eliminar todos los registros en hardware que tengan este tipo de hardware
                delete_hardware_query = "DELETE FROM hardware WHERE Hardware_type_Id = %s"
                cursor.execute(delete_hardware_query, (type_id,))
                
                # Eliminar el tipo de hardware por su ID
                delete_type_query = "DELETE FROM hardwaretypes WHERE type_id = %s"
                cursor.execute(delete_type_query, (type_id,))
                
                connection.commit()
                
            # Redirigir a la página de hardware_types después de eliminar
            return RedirectResponse(url='/hardware_types', status_code=303)
        except Exception as e:
            connection.rollback()
            return {"error": str(e)}


# Endpoint para mostrar la página de Location Code
@router.get("/location_code")
async def fetch_location_code(request: Request):
    # Obtener todos los location_code
    location_code = get_location_codes()

    # Obtener el estado is_active para cada hardware relacionado
    with get_connection_monedero() as db:
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT hardware.Localizacion, hardware.is_active
            FROM hardware
        """)
        hardware_status = cursor.fetchall()

    # Crear un diccionario con el estado de is_active por location_code
    location_status = {}
    for record in hardware_status:
        location_status[record["Localizacion"]] = record["is_active"]

    # Obtener la cookie is_admin de la sesión
    is_admin = request.cookies.get("is_admin") == "1"

    return templates.TemplateResponse(
        "location_code.html", 
        {"request": request, "location_code": location_code, "is_admin": is_admin, "location_status": location_status}
    )


# Endpoint para mostrar la página de agregar tipos de hardware
@router.get("/insert_location_code", response_class=HTMLResponse)
async def add_location_code_page(request: Request):

    return templates.TemplateResponse("insert_location_code.html", {"request": request})


# Endpoint para insertar un nuevo Location Code
@router.post("/insert_location_code")
async def add_location_code(id: str = Form(...), name: str = Form(...)):
    with get_connection_monedero() as db:
        success = insert_location_code(db, id, name)

    if success:
        return RedirectResponse(url="/insert_location_code?success=true", status_code=303)
    else:
        return RedirectResponse(url="/insert_location_code?error=exists", status_code=303)


# Endpoint para eliminar un Location Code
@router.post("/delete_location_code")
def delete_location_code(id: str = Form(...)):
    with get_connection_monedero() as connection:
        try:
            with connection.cursor() as cursor:
                # Eliminar los registros de hardware asociados al location_code (con LIKE)
                query_delete_hardware = "DELETE FROM hardware WHERE CodeName LIKE %s"
                cursor.execute(query_delete_hardware, (id + '%',))  # '%': Coincide con cualquier sufijo

                # Eliminar el location_code
                query_delete_location_code = "DELETE FROM location_code WHERE id = %s"
                cursor.execute(query_delete_location_code, (id,))
                
                # Commit de los cambios
                connection.commit()

            # Responder con un mensaje de éxito y redirección
            return {"message": "Location Code eliminado correctamente.", "redirect_url": "/location_code"}
        except Exception as e:
            connection.rollback()
            return {"error": f"Hubo un problema al intentar eliminar el Location Code: {str(e)}"}
        

# Endpoint para mostrar la página de insertar hardware
@router.get("/insert", response_class=HTMLResponse)
async def insert_hardware_page(request: Request):
    hardware_types = get_hardware_types()
    hardware = get_all_hardware()
    
    # Obtener todos los códigos de localización
    location_codes = get_location_codes()  # Obtener la lista de location_code
    
    # Obtener la cookie is_admin de la sesión
    is_admin = request.cookies.get("is_admin") == "1"
    
    return templates.TemplateResponse(
        "insert_hardware.html", 
        {
            "request": request,
            "hardware_types": hardware_types,
            "hardware": hardware,
            "is_admin": is_admin,
            "location_codes": location_codes
        }
    )


# Endpoint para insertar un nuevo hardware en la base de datos
@router.post("/insert")
async def insert_hardware_data(
    codeName: str = Form(...),
    IP: str = Form(...),
    nombre: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    hardware_type_id: int = Form(...),
    localizacion: str = Form(...),
    master_password: str = Form(...),
):
    # 1) Verificar que las contraseñas coinciden
    if password != confirm_password:
        return RedirectResponse(url="/insert?error=password_mismatch", status_code=303)

    # 2) Verificar la master password (descifrar "TEST MASTER KEY")
    try:
        with get_connection_monedero() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT ciphertext FROM master_check WHERE id=1")
                row = cursor.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="No se encontró el texto cifrado para verificación.")

                ciphertext = row["ciphertext"]
                test_plain = decrypt_with_master(ciphertext, master_password)

                if test_plain != "TEST MASTER KEY":
                    raise HTTPException(status_code=401, detail="Contraseña maestra incorrecta.")
    except Exception as e:
        return RedirectResponse(url="/insert?error=master_password_incorrect", status_code=303)

    # 3) Cifrar la contraseña del hardware con la master password proporcionada
    encrypted_password = encrypt_with_master(password, master_password)

    # 4) Insertar el hardware en la base de datos
    try:
        with get_connection_monedero() as conn:
            insert_hardware(conn, codeName, IP, nombre, encrypted_password, hardware_type_id, localizacion)
    except Exception as e:
        # Detectar IP duplicada (error 1062 es código de "duplicate entry" en MySQL)
        if "1062" in str(e) and "IP" in str(e):
            return RedirectResponse(url="/insert?error=ip_exists", status_code=303)
        return RedirectResponse(url="/insert?error=db_error", status_code=303)

    # 5) Redirección con éxito
    return RedirectResponse(url="/insert?success=true", status_code=303)


@router.get("/insert_email", response_class=HTMLResponse)
async def insert_email_page(request: Request):
    return templates.TemplateResponse("insert_email.html", {"request": request})


@router.post("/insert_email")
async def insert_email_data(
    email: str = Form(...),
    grupo: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    master_password: str = Form(...),
):
    valid_groups = {"Facebook", "YouTube", "Instagram", "Twitter", "TikTok"}
    if grupo not in valid_groups:
        return RedirectResponse(url="/insert_email?error=invalid_group", status_code=303)

    if password != confirm_password:
        return RedirectResponse(url="/insert_email?error=password_mismatch", status_code=303)

    # Validar master password con TEST MASTER KEY
    try:
        with get_connection_monedero() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT ciphertext FROM master_check WHERE id=1")
                row = cursor.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Texto de verificación no encontrado.")

                test_plain = decrypt_with_master(row["ciphertext"], master_password)
                if test_plain != "TEST MASTER KEY":
                    raise HTTPException(status_code=401, detail="Contraseña maestra incorrecta.")
    except Exception:
        return RedirectResponse(url="/insert_email?error=master_password_incorrect", status_code=303)

    with get_connection_monedero() as db:
        if get_email_by_email(db, email):
            return RedirectResponse(url="/insert_email?error=email_exists", status_code=303)

        encrypted_password = encrypt_with_master(password, master_password)
        insert_email(db, email, grupo, encrypted_password)

    return RedirectResponse(url="/insert_email?success=true", status_code=303)


@router.delete("/delete_email/{email_id}")
async def delete_email(email_id: int):
    with get_connection_monedero() as db:
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM emails WHERE id = %s", (email_id,))
            db.commit()
            return RedirectResponse(url="/emails", status_code=303)
        except Exception as e:
            db.rollback()
            return RedirectResponse(url="/emails?error=delete_failed", status_code=303)
        

@router.get("/verify-master-form", response_class=HTMLResponse)
async def show_verify_master_form(request: Request):
    return templates.TemplateResponse("verify_master.html", {
        "request": request,
        "error": None
    })


@router.post("/verify-master-current")
async def verify_master_current(request: Request, current_password: str = Form(...)):
    templates = Jinja2Templates(directory="app/templates")

    try:
        with get_connection_monedero() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT ciphertext FROM master_check WHERE id = 1")
                row = cursor.fetchone()
                if not row:
                    return templates.TemplateResponse("verify_master.html", {
                        "request": request,
                        "error": "No se encontró el bloque de verificación."
                    })

                ciphertext = row["ciphertext"]
                decrypted = decrypt_with_master(ciphertext, current_password)
                if decrypted != "TEST MASTER KEY":
                    raise ValueError("Texto descifrado inválido.")
    except Exception:
        return templates.TemplateResponse("verify_master.html", {
            "request": request,
            "error": "Contraseña maestra incorrecta."
        })

    # Redirige al formulario sin poner la contraseña en la URL
    response = RedirectResponse(url="/change-master-form", status_code=303)
    response.set_cookie(
        key="old_master_password",
        value=current_password,
        httponly=True,  # no accesible por JS
        samesite="Lax",
        max_age=300,  # caduca en 5 minutos
        path="/"
    )
    return response


@router.get("/change-master-form")
async def show_change_form(request: Request):
    templates = Jinja2Templates(directory="app/templates")
    old_password = request.cookies.get("old_master_password")
    
    if not old_password:
        return RedirectResponse(url="/verify-master-form", status_code=303)
    
    return templates.TemplateResponse("change_master.html", {
        "request": request,
        "old_password": old_password
    })


@router.post("/change-master-password")
async def change_master_password(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    templates = Jinja2Templates(directory="app/templates")

    if new_password != confirm_password:
        return templates.TemplateResponse("change_master.html", {
            "request": request,
            "old_password": old_password,
            "error": "Las nuevas contraseñas no coinciden."
        })

    try:
        with get_connection_monedero() as conn:
            with conn.cursor() as cursor:
                # Verificar master password
                cursor.execute("SELECT ciphertext FROM master_check WHERE id = 1")
                row = cursor.fetchone()
                decrypted = decrypt_with_master(row["ciphertext"], old_password)
                if decrypted != "TEST MASTER KEY":
                    raise ValueError("Master password inválida")

                # REENCRIPTAR HARDWARE
                cursor.execute("SELECT id, password_hash FROM hardware")
                all_hardware = cursor.fetchall()

                decrypted_hardware = []
                for hw in all_hardware:
                    try:
                        plain = decrypt_with_master(hw["password_hash"], old_password)
                        decrypted_hardware.append((hw["id"], plain))
                    except Exception:
                        raise Exception(f"Error al descifrar hardware ID {hw['id']}")

                for hw_id, plain in decrypted_hardware:
                    new_encrypted = encrypt_with_master(plain, new_password)
                    cursor.execute("UPDATE hardware SET password_hash=%s WHERE id=%s", (new_encrypted, hw_id))

                # REENCRIPTAR EMAILS
                cursor.execute("SELECT id, password_hash FROM emails")
                all_emails = cursor.fetchall()

                decrypted_emails = []
                for email in all_emails:
                    try:
                        plain = decrypt_with_master(email["password_hash"], old_password)
                        decrypted_emails.append((email["id"], plain))
                    except Exception:
                        raise Exception(f"Error al descifrar email ID {email['id']}")

                for email_id, plain in decrypted_emails:
                    new_encrypted = encrypt_with_master(plain, new_password)
                    cursor.execute("UPDATE emails SET password_hash=%s WHERE id=%s", (new_encrypted, email_id))

                # ACTUALIZAR MASTER_CHECK
                new_ciphertext = encrypt_with_master("TEST MASTER KEY", new_password)
                cursor.execute("UPDATE master_check SET ciphertext=%s WHERE id=1", (new_ciphertext,))
                conn.commit()

    except Exception as e:
        return templates.TemplateResponse("change_master.html", {
            "request": request,
            "old_password": old_password,
            "error": f"Error al cambiar la contraseña maestra: {e}"
        })

    response = RedirectResponse(url="/?success=master_password_changed", status_code=303)
    response.delete_cookie("old_master_password")
    return response