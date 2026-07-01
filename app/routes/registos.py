from io import BytesIO
from math import ceil
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, send_file, session, url_for
from openpyxl import Workbook

from app.database import (
    contar_registos,
    get_registo_por_id,
    inserir_registo,
    listar_registos,
    listar_todos_registos,
    registrar_log,
    registrar_saida,
)
from app.utils.permissions import tem_permissao, tipos_registo_permitidos
from app.utils.validators import validar_departamento, validar_identificacao, validar_nome
from config import PER_PAGE

registos_bp = Blueprint("registos", __name__)


def _requer_login():
    if not session.get("operador_id"):
        return redirect(url_for("auth.login"))
    return None


def _requer_permissao(permissao):
    if not tem_permissao(session.get("operador_tipo"), permissao):
        flash("Não tem permissão para esta ação.", "erro")
        return redirect(url_for("registos.menu"))
    return None


def _filtros_da_request():
    tipo = request.args.get("tipo", "").strip() or None
    tipos_permitidos = tipos_registo_permitidos(session.get("operador_tipo"))
    if tipo and tipo not in tipos_permitidos:
        tipo = None

    return {
        "nome": request.args.get("nome", "").strip() or None,
        "data": request.args.get("data", "").strip() or None,
        "tipo": tipo,
        "apenas_dentro": request.args.get("apenas_dentro") == "1",
    }


def _detalhes_registo(dados):
    partes = [f"tipo={dados['tipo']}", f"nome={dados['nome']}", f"id={dados['identificacao']}"]
    if dados.get("departamento"):
        partes.append(f"dept={dados['departamento']}")
    if dados.get("motivo_visita"):
        partes.append(f"motivo={dados['motivo_visita']}")
    if dados.get("funcionario_visitado"):
        partes.append(f"visitado={dados['funcionario_visitado']}")
    return " | ".join(partes)


@registos_bp.route("/menu")
def menu():
    redirecionar = _requer_login()
    if redirecionar:
        return redirecionar

    filtros = _filtros_da_request()
    pagina = max(int(request.args.get("pagina", 1)), 1)
    total = contar_registos(**filtros)
    total_paginas = max(ceil(total / PER_PAGE), 1)
    registos = listar_registos(**filtros, limite=PER_PAGE, pagina=pagina)

    return render_template(
        "menu.html",
        operador_nome=session.get("operador_nome"),
        operador_tipo=session.get("operador_tipo"),
        registos=registos,
        filtros=filtros,
        pagina=pagina,
        total_paginas=total_paginas,
        total=total,
        per_page=PER_PAGE,
        pode_funcionario=tem_permissao(session.get("operador_tipo"), "menu_funcionario"),
        pode_estagiario=tem_permissao(session.get("operador_tipo"), "menu_estagiario"),
        pode_visitante=tem_permissao(session.get("operador_tipo"), "menu_visitante"),
        pode_exportar=tem_permissao(session.get("operador_tipo"), "exportar"),
        pode_saida=tem_permissao(session.get("operador_tipo"), "registar_saida"),
        pode_comprovante=tem_permissao(session.get("operador_tipo"), "comprovante"),
        tipos_filtro=tipos_registo_permitidos(session.get("operador_tipo")),
    )


@registos_bp.route("/exportar_excel")
def exportar_excel():
    redirecionar = _requer_login() or _requer_permissao("exportar")
    if redirecionar:
        return redirecionar

    filtros = _filtros_da_request()
    registos = listar_todos_registos(**filtros)

    wb = Workbook()
    ws = wb.active
    ws.title = "Registos de Acesso"
    ws.append([
        "ID", "Entrada", "Saída", "Tipo", "Nome", "Identificação",
        "Departamento", "Motivo da Visita", "É Familiar",
        "Funcionário Visitado", "Operador", "Tipo Operador",
    ])

    for r in registos:
        ws.append([
            r["id"], r["registrado_em"], r.get("saida_em") or "",
            r["tipo"], r["nome"], r["identificacao"],
            r.get("departamento") or "", r.get("motivo_visita") or "",
            "Sim" if r.get("eh_familiar") else "Não",
            r.get("funcionario_visitado") or "",
            r["operador_nome"], r["operador_tipo"],
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    nome_ficheiro = f"registos_acesso_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    registrar_log(
        operador_id=session["operador_id"],
        operador_nome=session["operador_nome"],
        acao="exportar_excel",
        detalhes=f"Exportados {len(registos)} registos",
    )

    return send_file(
        buffer,
        as_attachment=True,
        download_name=nome_ficheiro,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@registos_bp.route("/registar/saida/<int:registo_id>", methods=["POST"])
def registar_saida_route(registo_id):
    redirecionar = _requer_login() or _requer_permissao("registar_saida")
    if redirecionar:
        return redirecionar

    registo = get_registo_por_id(registo_id)
    if not registo:
        flash("Registo não encontrado.", "erro")
        return redirect(url_for("registos.menu"))

    if registo.get("saida_em"):
        flash("Saída já registada para este acesso.", "erro")
        return redirect(url_for("registos.menu"))

    registrar_saida(registo_id)
    registrar_log(
        operador_id=session["operador_id"],
        operador_nome=session["operador_nome"],
        acao="registar_saida",
        detalhes=f"id={registo_id}, nome={registo['nome']}",
    )
    flash(f"Saída de {registo['nome']} registada com sucesso.", "sucesso")
    return redirect(url_for("registos.menu"))


@registos_bp.route("/comprovante/<int:registo_id>")
def comprovante(registo_id):
    redirecionar = _requer_login() or _requer_permissao("comprovante")
    if redirecionar:
        return redirecionar

    registo = get_registo_por_id(registo_id)
    if not registo:
        flash("Registo não encontrado.", "erro")
        return redirect(url_for("registos.menu"))

    return render_template("comprovante.html", registo=registo)


@registos_bp.route("/registar/funcionario", methods=["POST"])
def registar_funcionario():
    redirecionar = _requer_login() or _requer_permissao("menu_funcionario")
    if redirecionar:
        return redirecionar

    ok_nome, nome = validar_nome(request.form.get("nome"))
    ok_id, identificacao = validar_identificacao(request.form.get("identificacao"), "Funcionario")
    ok_dept, departamento = validar_departamento(request.form.get("departamento"))

    if not ok_nome or not ok_id or not ok_dept:
        flash(nome if not ok_nome else identificacao if not ok_id else departamento, "erro")
        return redirect(url_for("registos.menu"))

    dados = {
        "tipo": "Funcionario", "nome": nome, "identificacao": identificacao,
        "departamento": departamento, "operador_id": session["operador_id"],
    }
    inserir_registo(dados)
    registrar_log(
        operador_id=session["operador_id"], operador_nome=session["operador_nome"],
        acao="registo_funcionario", detalhes=_detalhes_registo(dados),
    )
    flash(f"Funcionário {nome} registado com sucesso.", "sucesso")
    return redirect(url_for("registos.menu"))


@registos_bp.route("/registar/estagiario", methods=["POST"])
def registar_estagiario():
    redirecionar = _requer_login() or _requer_permissao("menu_estagiario")
    if redirecionar:
        return redirecionar

    ok_nome, nome = validar_nome(request.form.get("nome"))
    ok_id, identificacao = validar_identificacao(request.form.get("identificacao"), "Estagiario")
    ok_dept, departamento = validar_departamento(request.form.get("departamento"))

    if not ok_nome or not ok_id or not ok_dept:
        flash(nome if not ok_nome else identificacao if not ok_id else departamento, "erro")
        return redirect(url_for("registos.menu"))

    dados = {
        "tipo": "Estagiario", "nome": nome, "identificacao": identificacao,
        "departamento": departamento, "operador_id": session["operador_id"],
    }
    inserir_registo(dados)
    registrar_log(
        operador_id=session["operador_id"], operador_nome=session["operador_nome"],
        acao="registo_estagiario", detalhes=_detalhes_registo(dados),
    )
    flash(f"Estagiário {nome} registado com sucesso.", "sucesso")
    return redirect(url_for("registos.menu"))


@registos_bp.route("/registar/visitante", methods=["POST"])
def registar_visitante():
    redirecionar = _requer_login() or _requer_permissao("menu_visitante")
    if redirecionar:
        return redirecionar

    ok_nome, nome = validar_nome(request.form.get("nome"))
    ok_id, identificacao = validar_identificacao(request.form.get("identificacao"), "Visitante")
    eh_familiar = request.form.get("eh_familiar") == "sim"

    if not ok_nome or not ok_id:
        flash(nome if not ok_nome else identificacao, "erro")
        return redirect(url_for("registos.menu"))

    dados = {
        "tipo": "Visitante", "nome": nome, "identificacao": identificacao,
        "eh_familiar": 1 if eh_familiar else 0, "operador_id": session["operador_id"],
    }

    if eh_familiar:
        ok_nome_func, funcionario_visitado = validar_nome(request.form.get("funcionario_visitado"))
        if not ok_nome_func:
            flash(funcionario_visitado, "erro")
            return redirect(url_for("registos.menu"))
        dados["funcionario_visitado"] = funcionario_visitado
    else:
        motivo_visita = request.form.get("motivo_visita", "").strip()
        ok_dept, departamento = validar_departamento(request.form.get("departamento"))
        if not motivo_visita or not ok_dept:
            flash("Preencha o motivo da visita e um departamento válido.", "erro")
            return redirect(url_for("registos.menu"))
        dados["motivo_visita"] = motivo_visita
        dados["departamento"] = departamento

    inserir_registo(dados)
    registrar_log(
        operador_id=session["operador_id"], operador_nome=session["operador_nome"],
        acao="registo_visitante", detalhes=_detalhes_registo(dados),
    )
    flash(f"Visitante {nome} registado com sucesso.", "sucesso")
    return redirect(url_for("registos.menu"))
