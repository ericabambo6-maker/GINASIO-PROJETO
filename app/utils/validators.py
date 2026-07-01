import re

BI_PATTERN = re.compile(r"^[A-Za-z0-9]{5,20}$")
CARTAO_PATTERN = re.compile(r"^[A-Za-z0-9\-]{3,30}$")


def validar_nome(nome):
    nome = (nome or "").strip()
    if len(nome) < 2:
        return False, "O nome deve ter pelo menos 2 caracteres."
    if len(nome) > 120:
        return False, "O nome é demasiado longo."
    return True, nome


def validar_identificacao(identificacao, tipo_pessoa):
    identificacao = (identificacao or "").strip()
    if not identificacao:
        return False, "A identificação é obrigatória."

    if tipo_pessoa == "Visitante":
        if not BI_PATTERN.match(identificacao):
            return False, "BI/Passaporte inválido (use 5 a 20 caracteres alfanuméricos)."
    else:
        if not CARTAO_PATTERN.match(identificacao):
            return False, "Número de cartão inválido."

    return True, identificacao


def validar_departamento(departamento):
    departamento = (departamento or "").strip()
    if len(departamento) < 2:
        return False, "O departamento deve ter pelo menos 2 caracteres."
    return True, departamento


def validar_usuario(usuario):
    usuario = (usuario or "").strip().lower()
    if not re.match(r"^[a-z0-9_]{3,30}$", usuario):
        return False, "Utilizador inválido (3-30 caracteres: letras, números, _)."
    return True, usuario


def validar_senha(senha):
    if len(senha or "") < 6:
        return False, "A senha deve ter pelo menos 6 caracteres."
    return True, senha
