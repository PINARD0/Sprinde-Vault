import pymysql
from security import encrypt_with_master

# Ajusta estos valores a tu entorno
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "1234"
DB_NAME = "MonederoPW"

def initialize_master_check(master_password: str):
    # 1) Conexión a la BD
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # 2) Crear la tabla "master_check" si no existe
            #    Solo necesitamos un ID fijo (ej: 1) y un campo para el ciphertext
            create_table_query = """
                CREATE TABLE IF NOT EXISTS master_check (
                    id INT PRIMARY KEY,
                    ciphertext TEXT NOT NULL
                )
            """
            cursor.execute(create_table_query)

            # 3) Ciframos un texto fijo con la master password
            plain_text = "TEST MASTER KEY"  # o el que tú quieras
            encrypted_text = encrypt_with_master(plain_text, master_password)

            # 4) Insertamos/actualizamos la fila con ID = 1
            #    Así nos aseguramos de que solo haya un registro
            upsert_query = """
                INSERT INTO master_check (id, ciphertext)
                VALUES (1, %s)
                ON DUPLICATE KEY UPDATE
                    ciphertext = VALUES(ciphertext)
            """
            cursor.execute(upsert_query, (encrypted_text,))
            connection.commit()

            print("Tabla master_check inicializada correctamente.")
    except Exception as e:
        print("Error al inicializar master_check:", e)
    finally:
        connection.close()

if __name__ == "__main__":
    # Pedimos al usuario la master password
    master_pass = input("Introduce la master password por primera vez: ")
    initialize_master_check(master_pass)
    print("¡Setup completado! Ahora puedes borrar este script si quieres.")