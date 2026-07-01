from math import ceil

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from app.database import (
    alterar_senha_operador,
    atualizar_operador,
    contar_logs,
    criar_operador,
    get_operador_por_id,
    listar_logs,
    listar_operadores,
    obter_estatisticas_dashboard,
    registrar_log,
)
from app.utils.backup import criar_backup
from app.utils.permissions import tem_permissao
from app.utils.validators import validar_nome, validar_senha, validar_usuario
from config import PER_PAGE

admin_bp = Blueprint("admin", __name__)


def _requer_login():
    if not session.get("operador_id"):
        return redirect(url_for("auth.login"))
    return None


def _requer_permissao(permissao):
    if not tem_permissao(session.get("operador_tipo"), permissao):
        flash("Não tem permissão para aceder a esta área.", "erro")
        return redirect(url_for("registos.menu"))
    return None


@admin_bp.route("/dashboard")
def dashboard():
    redirecionar = _requer_login() or _requer_permissao("dashboard")
    if redirecionar:
        return redirecionar

    stats = obter_estatisticas_dashboard()
    return render_template("dashboard.html", stats=stats)


@admin_bp.route("/operadores")
def operadores():
    redirecionar = _requer_login() or _requer_permissao("gerir_operadores")
    if redirecionar:
        return redirecionar

    return render_template(
        "admin_operadores.html",
        operadores=listar_operadores(),
        tipos_operador=("Policia", "Admin", "RH"),
    )


@admin_bp.route("/operadores/criar", methods=["POST"])
def criar_operador_route():
    redirecionar = _requer_login() or _requer_permissao("gerir_operadores")
    if redirecionar:
        return redirecionar

    ok_nome, nome = validar_nome(request.form.get("nome"))
    ok_usuario, usuario = validar_usuario(request.form.get("usuario"))
    ok_senha, senha = validar_senha(request.form.get("senha"))
    tipo = request.form.get("tipo", "").strip()

    if not ok_nome or not ok_usuario or not ok_senha:
        flash(nome if not ok_nome else usuario if not ok_usuario else senha, "erro")
        return redirect(url_for("admin.operadores"))

    if tipo not in ("Policia", "Admin", "RH"):
        flash("Tipo de operador inválido.", "erro")
        return redirect(url_for("admin.operadores"))

    try:
        criar_operador(nome, usuario, senha, tipo)
        registrar_log(
            operador_id=session["operador_id"],
            operador_nome=session["operador_nome"],
            acao="criar_operador",
            detalhes=f"usuario={usuario}, tipo={tipo}",
        )
        flash(f"Operador {nome} criado com sucesso.", "sucesso")
    except Exception:
        flash("Não foi possível criar o operador. Utilizador já existe?", "erro")

    return redirect(url_for("admin.operadores"))


@admin_bp.route("/operadores/<int:operador_id>/editar", methods=["POST"])
def editar_operador_route(operador_id):
    redirecionar = _requer_login() or _requer_permissao("gerir_operadores")
    if redirecionar:
        return redirecionar

    ok_nome, nome = validar_nome(request.form.get("nome"))
    ok_usuario, usuario = validar_usuario(request.form.get("usuario"))
    tipo = request.form.get("tipo", "").strip()
    ativo = 1 if request.form.get("ativo") == "1" else 0

    if not ok_nome or not ok_usuario:
        flash(nome if not ok_nome else usuario, "erro")
        return redirect(url_for("admin.operadores"))

    if tipo not in ("Policia", "Admin", "RH"):
        flash("Tipo de operador inválido.", "erro")
        return redirect(url_for("admin.operadores"))

    atualizar_operador(operador_id, nome, usuario, tipo, ativo)
    registrar_log(
        operador_id=session["operador_id"],
        operador_nome=session["operador_nome"],
        acao="editar_operador",
        detalhes=f"id={operador_id}, usuario={usuario}, ativo={ativo}",
    )
    flash("Operador atualizado com sucesso.", "sucesso")
    return redirect(url_for("admin.operadores"))


@admin_bp.route("/logs")
def logs():
    redirecionar = _requer_login() or _requer_permissao("ver_logs")
    if redirecionar:
        return redirecionar

    pagina = max(int(request.args.get("pagina", 1)), 1)
    total = contar_logs()
    logs_lista = listar_logs(limite=PER_PAGE, pagina=pagina)
    total_paginas = max(ceil(total / PER_PAGE), 1)

    return render_template(
        "admin_logs.html",
        logs=logs_lista,
        pagina=pagina,
        total_paginas=total_paginas,
        total=total,
    )


@admin_bp.route("/backup")
def backup():
    redirecionar = _requer_login() or _requer_permissao("backup")
    if redirecionar:
        return redirecionar

    caminho = criar_backup()
    registrar_log(
        operador_id=session["operador_id"],
        operador_nome=session["operador_nome"],
        acao="backup_bd",
        detalhes=caminho,
    )
    flash(f"Backup criado: {caminho}", "sucesso")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/alterar-senha", methods=["GET", "POST"])
def alterar_senha():
    redirecionar = _requer_login() or _requer_permissao("alterar_senha")
    if redirecionar:
        return redirecionar

    if request.method == "POST":
        senha_atual = request.form.get("senha_atual", "")
        nova_senha = request.form.get("nova_senha", "")
        confirmar = request.form.get("confirmar_senha", "")

        operador = get_operador_por_id(session["operador_id"])
        if not operador or not check_password_hash(operador["senha_hash"], senha_atual):
            flash("Senha atual incorreta.", "erro")
            return redirect(url_for("admin.alterar_senha"))

        ok_senha, msg = validar_senha(nova_senha)
        if not ok_senha:
            flash(msg, "erro")
            return redirect(url_for("admin.alterar_senha"))

        if nova_senha != confirmar:
            flash("A confirmação da senha não coincide.", "erro")
            return redirect(url_for("admin.alterar_senha"))

        alterar_senha_operador(session["operador_id"], nova_senha)
        registrar_log(
            operador_id=session["operador_id"],
            operador_nome=session["operador_nome"],
            acao="alterar_senha",
            detalhes="Senha alterada pelo operador",
        )
        flash("Senha alterada com sucesso.", "sucesso")
        return redirect(url_for("registos.menu"))

    return render_template("alterar_senha.html")
