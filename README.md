# 🔐 SprinVault - Gestor de Contraseñas

**SprinVault** es una aplicación desarrollada con **Python** y **FastAPI** que permite gestionar de forma segura contraseñas de usuarios, dispositivos hardware y cuentas de correo. Está diseñada para entornos administrados y controlados, con funcionalidades avanzadas como la protección mediante una contraseña maestra que nunca se guarda en la base de datos.

---

## 🚀 Características principales

### 👥 Gestión de Usuarios
- Añadir nuevos usuarios.
- Eliminar usuarios (solo si eres admin).

### 🛠️ Gestión de Hardware
- Añadir, eliminar y modificar hardware (solo si eres admin).
- Visualizar contraseñas de hardware desencriptadas (requiere ingresar correctamente la **contraseña maestra**).
- Las contraseñas se almacenan encriptadas con AES-256.

### 🌍 Location Code
- Visualización completa de la tabla de códigos de localización.
- Permite desactivar registros asociados a un código.
- Los registros solo pueden eliminarse si están desactivados.

### 📧 Gestión de Correos
- Añadir y eliminar correos (solo si eres admin).
- Visualizar contraseñas de correo (requiere la **contraseña maestra**).

### 🔒 Contraseña Maestra
- La contraseña maestra **no se guarda en la base de datos**.
- Se usa para encriptar y desencriptar contraseñas de hardware y correos.
- Al cambiar la contraseña maestra:
  - Todas las contraseñas son desencriptadas y reencriptadas con la nueva.
  - El `ciphertext` asociado también se actualiza para validar la nueva clave.

---

## 🧰 Tecnologías utilizadas

- [Python](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [Docker](https://www.docker.com/products/docker-desktop)
- JWT para autenticación con access/refresh tokens

---

## ⚙️ Instalación y ejecución

### Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/sprinbault.git
cd sprinbault
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

> Este comando instalará todas las dependencias necesarias para el proyecto.

### Generar archivo `requirements.txt` (si has añadido nuevas dependencias)

```bash
pip freeze > requirements.txt
```

---

## 🐳 Ejecutar con Docker

Si usas Docker Desktop, puedes iniciar la aplicación con:

```bash
docker compose up --build -d
```

Esto levantará la app y sus servicios definidos en `docker-compose.yml`.

---

## 🔁 Ejecutar con Uvicorn

Para permitir que cualquier dispositivo en la red local acceda a la app:

```bash
uvicorn main:app --host 192.168.200.49 --port 8000 --reload
```

> Asegúrate de que la IP coincide con la IP local de tu PC.

Solo para uso local en tu dispositivo:

```bash
uvicorn main:app --reload
```

---

## 🔐 Seguridad

- Las contraseñas de usuarios se almacenan hasheadas.
- Las contraseñas de hardware y correos se encriptan con AES-256 usando una **clave maestra temporal**.
- El token JWT de acceso expira cada 10 minutos y se renueva automáticamente.
- Solo los administradores tienen permisos para modificar registros sensibles.

---

## 🗄️ Backups automáticos

SprinVault incluye un sistema para generar **backups automáticos semanales** de las bases de datos `MonederoPW` y `SprindeUserAuthDatabase`.


### 🧪 Script de backup

El script `backup_runner.py`:

- Crea un archivo `.sql` de cada base de datos usando `mysqldump`.
- Guarda los archivos en la carpeta `backups/`.
- Elimina automáticamente los backups que tengan más de **30 días** de antigüedad.


### 🖥️ Cómo programar backups semanales en Windows

1. Abre el **Programador de Tareas** (Task Scheduler).
2. Crea una nueva tarea:
   - Ejecutar con privilegios elevados.
   - Establece un desencadenador semanal (por ejemplo, todos los domingos a las 03:00).
3. Acción → Iniciar un programa:
   - **Programa/script**: ruta de tu `python.exe`.
   - **Agregar argumentos**: ruta completa a `backup_runner.py`.

> 💡 Asegúrate de que la ruta a `mysqldump.exe` en el script es correcta. Suele estar en  
> `C:\Archivos de programa\MySQL\MySQL Server 8.0\bin\`.


### 🧪 Verificación manual

Puedes ejecutar manualmente la tarea desde el Programador de Tareas,  
o correr el script desde la terminal:

```bash
python backup_runner.py
