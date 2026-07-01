import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

SECRET_KEY = os.environ.get("STAE_SECRET_KEY", "stae-dev-key-alterar-em-producao")
DEBUG = os.environ.get("STAE_DEBUG", "false").lower() in ("1", "true", "yes")
DATABASE_PATH = os.path.join(DATA_DIR, "stae_acesso.db")

DEMO_ACCOUNTS = [
    {
        "nome": "Administrador STAE",
        "usuario": os.environ.get("STAE_DEMO_ADMIN_USER", "admin"),
        "senha": os.environ.get("STAE_DEMO_ADMIN_PASSWORD", "admin123"),
        "tipo": "Admin",
    },
    {
        "nome": "Operador Polícia",
        "usuario": os.environ.get("STAE_DEMO_POLICIA_USER", "policia"),
        "senha": os.environ.get("STAE_DEMO_POLICIA_PASSWORD", "policia123"),
        "tipo": "Policia",
    },
    {
        "nome": "Operador RH",
        "usuario": os.environ.get("STAE_DEMO_RH_USER", "rh"),
        "senha": os.environ.get("STAE_DEMO_RH_PASSWORD", "rh123"),
        "tipo": "RH",
    },
]

LOGIN_MAX_ATTEMPTS = int(os.environ.get("STAE_LOGIN_MAX_ATTEMPTS", "5"))
LOGIN_LOCKOUT_SECONDS = int(os.environ.get("STAE_LOGIN_LOCKOUT_SECONDS", "900"))
PER_PAGE = int(os.environ.get("STAE_PER_PAGE", "15"))
HOST = os.environ.get("STAE_HOST", "127.0.0.1")
PORT = int(os.environ.get("STAE_PORT", "5000"))
