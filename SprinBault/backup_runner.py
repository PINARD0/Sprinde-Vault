# backup_runner.py
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import os

BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

def create_backup(database_name: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = BACKUP_DIR / f"{database_name}_{timestamp}.sql"

    try:
        # Ajusta la ruta si tienes MySQL en otro lugar
        command = f'"C:\\Archivos de programa\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe" -u root -p1234 {database_name} > "{backup_filename}"'
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[✓] Backup de {database_name} creado en {backup_filename}")
        else:
            print(f"[✗] Error al crear el backup de {database_name}: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"[✗] Error al ejecutar el comando mysqldump: {e}")

def delete_old_backups():
    now = datetime.now()
    for file in BACKUP_DIR.iterdir():
        if file.is_file():
            file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if now - file_mtime > timedelta(days=30):
                try:
                    os.remove(file)
                    print(f"[🗑️] Backup antiguo eliminado: {file}")
                except Exception as e:
                    print(f"[✗] No se pudo eliminar el archivo {file}: {e}")

def main():
    create_backup("MonederoPW")
    create_backup("SprindeUserAuthDatabase")
    delete_old_backups()

if __name__ == "__main__":
    main()