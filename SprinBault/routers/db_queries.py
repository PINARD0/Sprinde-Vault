import base64
import pymysql
from database import get_connection_sprinde, get_connection_monedero

# Función para insertar un nuevo usuario en la base de datos con is_admin = 0 (usuario normal).
def insert_user(email, password_hash):
    # Paso 1: Buscar el ID disponible más bajo
    query = "SELECT id FROM users ORDER BY id ASC"
    with get_connection_sprinde() as conn:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            existing_ids = [row['id'] for row in cursor.fetchall()]

    # Paso 2: Encontrar el ID disponible más bajo
    new_id = 1
    while new_id in existing_ids:
        new_id += 1  # Incrementar hasta encontrar el ID disponible

    # Paso 3: Insertar el nuevo usuario con el ID disponible más bajo
    query = """
    INSERT INTO users (id, email, password_hash, created_at, is_admin)
    VALUES (%s, %s, %s, NOW(), 0)
    """
    with get_connection_sprinde() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (new_id, email, password_hash))
        conn.commit()

    return True  # Si se insertó correctamente
        
# Función para guardar una contraseña cifrada para un usuario en la base de datos
def save_password_for_user(email, hashed_password):
    query = "UPDATE users SET password_hash = %s WHERE email = %s"
    with get_connection_sprinde() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (hashed_password, email))
        conn.commit()


# Función para obtener un usuario por su email
def get_user_by_email(email):
    query = "SELECT * FROM users WHERE email = %s"
    with get_connection_sprinde() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (email,))
            return cursor.fetchone()

# Función para borrar usuarios por su ID
def delete_user_by_id(user_id: int):
    query = "DELETE FROM users WHERE id = %s"
    try:
        with get_connection_sprinde() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                conn.commit()
                return cursor.rowcount > 0  # Retorna True si se eliminó un usuario
    except Exception as e:
        print(f"Error al eliminar el usuario: {e}")
        return False

# Función para obtener todos los usuarios de la tabla users
def get_all_users():
    with get_connection_sprinde() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, email, created_at FROM users")
            return cursor.fetchall()

# Función para obtener todos los dispositivos activos de la tabla hardware
def get_all_hardware():
    with get_connection_monedero() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT hardware.id, hardware.codeName, hardware.IP, hardware.nombre, 
                       hardware.Localizacion, hardwaretypes.type_name 
                FROM hardware
                JOIN hardwaretypes ON hardware.Hardware_type_Id = hardwaretypes.type_id
                WHERE hardware.is_active = 1
            """)
            return cursor.fetchall()
        
# Función para obtener todos los correos
def get_all_emails():
    with get_connection_monedero() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, email, grupo FROM emails")
            return cursor.fetchall()

# Función para obtener la contraseña de un hardware
def get_hardware_password(hardware_id):
    query = "SELECT password_hash FROM hardware WHERE id = %s"
    with get_connection_monedero() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (hardware_id,))
            result = cursor.fetchone()

            if result is None:
                return None  # Si no se encuentra el hardware, retorna None

            return result

# Función para obtener todos los tipos de hardware
def get_hardware_types():
    with get_connection_monedero() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT type_id, type_name FROM hardwaretypes")
            return cursor.fetchall()

def insert_hardware_types(db, type_name):
    # Paso 1: Buscar el ID disponible más bajo
    query = "SELECT type_id FROM hardwaretypes ORDER BY type_id ASC"
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(query)
        existing_ids = [row['type_id'] for row in cursor.fetchall()]

    # Paso 2: Encontrar el ID disponible más bajo
    new_id = 1
    while new_id in existing_ids:
        new_id += 1  # Incrementar hasta encontrar el ID disponible

    # Paso 3: Insertar el tipo de hardware con el ID disponible más bajo
    insert_query = "INSERT INTO hardwaretypes (type_id, type_name) VALUES (%s, %s)"
    with db.cursor() as cursor:
        cursor.execute(insert_query, (new_id, type_name))
        db.commit()

    return True

def get_location_codes():
    query = "SELECT id, name FROM location_code"
    with get_connection_monedero() as db:
        with db.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

def insert_location_code(db, id, name):
    # Verificar si ya existe el tipo de hardware
    query = "SELECT id FROM location_code WHERE id = %s"
    with db.cursor() as cursor:
        cursor.execute(query, (id,))
        result = cursor.fetchone()

        if result:  # Si ya existe, result no será None
            return False  # El tipo de hardware ya existe

        # Insertar nuevo tipo de hardware
        insert_query = "INSERT INTO location_code (id, name) VALUES (%s, %s)"
        cursor.execute(insert_query, (id, name))
        db.commit()
        return True
        
# Función para insertar un nuevo hardware en la base de datos
def insert_hardware(db, codeName, IP, nombre, password, hardware_type_id, localizacion):
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        # Paso 1: Buscar el ID disponible más bajo
        query = "SELECT id FROM hardware ORDER BY id ASC"
        cursor.execute(query)
        existing_ids = [row['id'] for row in cursor.fetchall()]

        # Paso 2: Encontrar el ID disponible más bajo
        new_id = 1
        while new_id in existing_ids:
            new_id += 1  # Incrementar hasta encontrar el ID disponible

        # Paso 3: Buscar el último CodeName para el codeName dado y obtener el número más bajo disponible
        query = """
        SELECT CodeName FROM hardware WHERE CodeName LIKE %s ORDER BY LENGTH(CodeName) DESC, CodeName DESC
        """
        cursor.execute(query, (f"{codeName}-%",))
        result = cursor.fetchall()

        # Paso 4: Encontrar el número más bajo para ese `codeName` y generar el nuevo número incremental
        if result:
            # Extraemos los números de CodeName, como A60-1, A60-2
            existing_numbers = [int(row['CodeName'].split('-')[-1]) for row in result]
            next_number = min(set(range(1, max(existing_numbers)+2)) - set(existing_numbers))
        else:
            # Si no hay registros, comienza con el número 1
            next_number = 1

        # Generar el nuevo CodeName (Ej: A60-1, A60-2...)
        new_code_name = f"{codeName}-{next_number}"

        # Paso 5: Insertar el hardware con el ID más bajo disponible
        query = """
        INSERT INTO hardware (id, CodeName, IP, nombre, password_hash, Hardware_type_Id, Localizacion) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (new_id, new_code_name, IP, nombre, password, hardware_type_id, localizacion))

    db.commit()
    
def get_email_by_email(db, email):
    """Verifica si un email ya existe en la tabla emails de MonederoPW"""
    with db.cursor() as cursor:
        cursor.execute("SELECT id FROM emails WHERE email = %s", (email,))
        return cursor.fetchone()  # Retorna None si no existe

def insert_email(db, email, grupo, hashed_password):
    # Paso 1: Buscar el ID disponible más bajo
    query = "SELECT id FROM emails ORDER BY id ASC"
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(query)
        existing_ids = [row['id'] for row in cursor.fetchall()]

    # Paso 2: Encontrar el ID disponible más bajo
    new_id = 1
    while new_id in existing_ids:
        new_id += 1  # Incrementar hasta encontrar el ID disponible

    # Paso 3: Insertar el usuario con el ID disponible más bajo
    query = """INSERT INTO emails (id, email, grupo, password_hash) VALUES (%s, %s, %s, %s)"""
    with db.cursor() as cursor:
        cursor.execute(query, (new_id, email, grupo, hashed_password))
    db.commit()
    
def get_email_password(email_id):
    query = "SELECT password_hash FROM emails WHERE id = %s"
    with get_connection_monedero() as db:
        with db.cursor() as cursor:
            cursor.execute(query, (email_id,))
            result = cursor.fetchone()
            return result  # Devuelve la contraseña del email