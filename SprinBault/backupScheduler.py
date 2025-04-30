# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.interval import IntervalTrigger
# from datetime import datetime, timedelta
# import os
# import subprocess
# from pathlib import Path
# from database import get_connection_sprinde, get_connection_monedero

# # Configura el directorio para almacenar los backups
# BACKUP_DIR = Path("backups")
# BACKUP_DIR.mkdir(exist_ok=True)

# # Función para hacer el backup de una base de datos
# def create_backup(database_name: str, connection_function):
#     """
#     Crea un backup de la base de datos MySQL.
#     """
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     backup_filename = BACKUP_DIR / f"{database_name}_{timestamp}.sql"
    
#     # Conectar a la base de datos
#     with connection_function() as connection:
#         try:
#             # Usar la ruta completa para mysqldump
#             command = f'"C:\\Archivos de programa\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe" -u root -p1234 {database_name} > {backup_filename}'
            
#             result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            
#             if result.returncode == 0:
#                 print(f"Backup de {database_name} creado en {backup_filename}")
#             else:
#                 print(f"Error al crear el backup de {database_name}: {result.stderr}")
#         except subprocess.CalledProcessError as e:
#             print(f"Error al crear el backup de {database_name}: {e}")

# # Función para eliminar los backups antiguos (más de un mes)
# def delete_old_backups():
#     """
#     Elimina los archivos de backup con más de 1 mes de antigüedad.
#     """
#     now = datetime.now()
#     for backup_file in os.listdir(BACKUP_DIR):
#         backup_path = BACKUP_DIR / backup_file
#         if backup_path.is_file():
#             file_mtime = datetime.fromtimestamp(backup_path.stat().st_mtime)
#             if now - file_mtime > timedelta(days=30):  # Si el archivo tiene más de 30 días
#                 try:
#                     os.remove(backup_path)
#                     print(f"Backup antiguo eliminado: {backup_path}")
#                 except Exception as e:
#                     print(f"Error al eliminar el backup {backup_path}: {e}")

# # Función para iniciar el programador de tareas
# def start_scheduler():
#     """
#     Inicia el programador de tareas.
#     """
#     scheduler = BackgroundScheduler()
#     print('SCHEDULER INICIADO')

#     # Programar el backup de cada base de datos cada mes
#     scheduler.add_job(
#         lambda: create_backup('SprindeUserAuthDatabase', get_connection_sprinde),
#         trigger=IntervalTrigger(weeks=1),  # Se ejecuta cada semana
#         id='backup_sprinde_user_auth',
#         name='Backup de SprindeUserAuthDatabase',
#         replace_existing=True
#     )

#     scheduler.add_job(
#         lambda: create_backup('MonederoPW', get_connection_monedero),
#         trigger=IntervalTrigger(weeks=1),  # Se ejecuta cada semana
#         id='backup_monedero_pw',
#         name='Backup de MonederoPW',
#         replace_existing=True
#     )

#     # Programar la eliminación de backups antiguos cada mes
#     scheduler.add_job(
#         delete_old_backups,
#         trigger=IntervalTrigger(days=30),  # Se ejecuta cada 4 semanas
#         id='delete_old_backups',
#         name='Eliminar backups antiguos',
#         replace_existing=True
#     )

#     # Iniciar el programador
#     scheduler.start()