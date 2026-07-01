import shutil
from datetime import datetime

from config import BACKUP_DIR, DATABASE_PATH


def criar_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = f"{BACKUP_DIR}/stae_acesso_{timestamp}.db"
    shutil.copy2(DATABASE_PATH, destino)
    return destino
