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
        "menu_funcionario",
        "menu_estagiario",
        "menu_visitante",
        "registar_saida",
    },
    "Supervisor": {
        "exportar",
        "dashboard",
        "gerir_operadores",
        "ver_logs",
        "backup",
        "alterar_senha",
        "comprovante",
        "menu_funcionario",
        "menu_estagiario",
        "menu_visitante",
        "registar_saida",
    },
    "RH": {
        "menu_funcionario",
        "menu_estagiario",
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
    # Polícia pode registrar todos os tipos
    if tipo_operador == "Policia":
        return ["Funcionario", "Estagiario", "Visitante"]
    # RH pode registrar funcionários e estagiários
    if tipo_operador == "RH":
        return ["Funcionario", "Estagiario"]
    # Admin e Supervisor podem registrar todos
    if tipo_operador in ["Admin", "Supervisor"]:
        return ["Funcionario", "Estagiario", "Visitante"]
    return []
