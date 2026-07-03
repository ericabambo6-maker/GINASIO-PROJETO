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
        "ver_detalhes_registo",
    },
    "Supervisor": {
        "exportar",
        "dashboard",
        "gerir_operadores",
        "ver_logs",
        "backup",
        "alterar_senha",
        "comprovante",
        "ver_detalhes_registo",
    },
    "RH": {
        "menu_funcionario",
        "menu_estagiario",
        "alterar_senha",
    },
    "Policia": {
        "menu_visitante",
        "alterar_senha",
        "registar_saida",
        "comprovante",
    },
}


def tem_permissao(tipo_operador, permissao):
    return permissao in PERMISSOES.get(tipo_operador, set())


def tipos_registo_permitidos(tipo_operador):
    # Polícia só pode registrar visitantes
    if tipo_operador == "Policia":
        return ["Visitante"]
    # RH pode registrar funcionários e estagiários
    if tipo_operador == "RH":
        return ["Funcionario", "Estagiario"]
    # Admin e Supervisor podem registrar todos
    if tipo_operador in ["Admin", "Supervisor"]:
        return ["Funcionario", "Estagiario", "Visitante"]
    return []
