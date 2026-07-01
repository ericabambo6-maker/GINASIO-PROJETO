import re
import shutil
from datetime import datetime

from config import BACKUP_DIR, DATABASE_PATH

PERMISSOES = {
    "Admin": {
        "exportar",
        "dashboard",
        "gerir_operadores",
        "ver_logs",
        "backup",
        "alterar_senha",
        "comprovante",
    },
    "RH": {
        "alterar_senha",
    },
    "Policia": {
        "menu_funcionario",
        "menu_estagiario",
        "menu_visitante",
        "alterar_senha",
        "registar_saida",
        "comprovante",
    },
}


def tem_permissao(tipo_operador, permissao):
    return permissao in PERMISSOES.get(tipo_operador, set())


def tipos_registo_permitidos(tipo_operador):
    return ["Funcionario", "Estagiario", "Visitante"]
