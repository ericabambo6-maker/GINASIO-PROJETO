import time

from flask import request

from config import LOGIN_LOCKOUT_SECONDS, LOGIN_MAX_ATTEMPTS

_attempts = {}


def _chave():
    return request.remote_addr or "local"


def esta_bloqueado():
    registo = _attempts.get(_chave())
    if not registo:
        return False, 0
    if registo["count"] >= LOGIN_MAX_ATTEMPTS:
        restante = int(registo["locked_until"] - time.time())
        if restante > 0:
            return True, restante
        _attempts.pop(_chave(), None)
    return False, 0


def registar_falha():
    registo = _attempts.get(_chave(), {"count": 0, "locked_until": 0})
    registo["count"] += 1
    if registo["count"] >= LOGIN_MAX_ATTEMPTS:
        registo["locked_until"] = time.time() + LOGIN_LOCKOUT_SECONDS
    _attempts[_chave()] = registo


def limpar_falhas():
    _attempts.pop(_chave(), None)
