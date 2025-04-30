from hashlib import pbkdf2_hmac
import bcrypt
from Crypto.Cipher import AES
import base64

# Función para hashear contraseñas
def hash_password(password: str) -> str:
    """Hashea la contraseña usando bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

# Función para verificar contraseñas hasheadas
def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica una contraseña hasheada."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# Opcional: puedes ajustar las iteraciones y el "pepper"/salt
ITERATIONS = 100_000


def derive_key(master_password: str, salt: bytes) -> bytes:
    """
    Deriva una clave de 32 bytes (AES-256) usando PBKDF2-HMAC-SHA256.
    - master_password: contraseña maestra introducida por el usuario
    - salt: puede ser un valor fijo (almacenado en un .env o en el código),
      o un salt único que guardes junto al ciphertext.
      Pero NUNCA guardes la clave derivada en la BBDD.
    """
    key = pbkdf2_hmac(
        hash_name='sha256',
        password=master_password.encode('utf-8'),
        salt=salt,
        iterations=ITERATIONS,
        dklen=32  # 32 bytes = 256 bits
    )
    return key


def encrypt_with_master(password_to_encrypt: str, master_password: str) -> str:
    """
    Cifra el 'password_to_encrypt' con AES-256, derivando la clave a partir
    de la 'master_password'. Retorna IV + ciphertext en Base64.
    """
    # 1) Usamos un salt fijo o cargado de un .env. Aquí se deja hardcodeado a modo de ejemplo
    SALT = b'SaltFijaDeEjemplo'

    key = derive_key(master_password, SALT)

    # 2) Creamos un cifrador AES en modo CBC. Generamos un IV aleatorio cada vez.
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv  # IV de 16 bytes

    # 3) Padding PKCS7
    block_size = 16
    pad_len = block_size - (len(password_to_encrypt) % block_size)
    padded_data = password_to_encrypt + chr(pad_len) * pad_len

    ciphertext = cipher.encrypt(padded_data.encode('utf-8'))

    # 4) Guardamos IV + ciphertext y todo eso a Base64
    encrypted_password = base64.b64encode(iv + ciphertext).decode('utf-8')
    return encrypted_password


def decrypt_with_master(encrypted_text: str, master_password: str) -> str:
    """
    Descifra un password en Base64 que fue cifrado con 'encrypt_with_master'.
    """
    SALT = b'SaltFijaDeEjemplo'  # Mismo salt que en encrypt_with_master
    key = derive_key(master_password, SALT)

    # 1) Decodificamos el base64 para obtener IV + ciphertext
    encrypted_data = base64.b64decode(encrypted_text)
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    # 2) Reconstruimos el cifrador AES
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # 3) Desciframos y retiramos el padding PKCS7
    decrypted_data = cipher.decrypt(ciphertext)
    pad_len = decrypted_data[-1]  # último byte
    decrypted_data = decrypted_data[:-pad_len]

    return decrypted_data.decode('utf-8')