from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from app.backend import get_operador_por_usuario, registrar_log
from app.utils.rate_limit import esta_bloqueado, limpar_falhas, registar_falha

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if session.get("operador_id"):
        return redirect(url_for("registos.menu"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    bloqueado, restante = esta_bloqueado()

    if request.method == "POST":
        if bloqueado:
            minutos = max(restante // 60, 1)
            erro = f"Muitas tentativas. Aguarde {minutos} minuto(s) e tente novamente."
            return render_template("login.html", erro=erro)

        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")
        operador = get_operador_por_usuario(usuario)

        if operador and check_password_hash(operador["senha_hash"], senha):
            limpar_falhas()
            session.clear()
            session["operador_id"] = operador["id"]
            session["operador_nome"] = operador["nome"]
            session["operador_tipo"] = operador["tipo"]
            registrar_log(
                operador_id=operador["id"],
                operador_nome=operador["nome"],
                acao="login",
                detalhes=f"Login bem-sucedido ({operador['tipo']})",
            )
            return redirect(url_for("registos.menu"))

        registar_falha()
        registrar_log(
            operador_nome=usuario,
            acao="login_falha",
            detalhes="Tentativa de login com credenciais inválidas",
        )
        erro = "Utilizador ou senha inválidos."

    return render_template("login.html", erro=erro)


@auth_bp.route("/logout")
def logout():
    if session.get("operador_id"):
        registrar_log(
            operador_id=session.get("operador_id"),
            operador_nome=session.get("operador_nome"),
            acao="logout",
            detalhes="Operador encerrou a sessão",
        )
    session.clear()
    return redirect(url_for("auth.login"))
