import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3  # Para o banco local real de testes
from contextlib import contextmanager
from werkzeug.security import generate_password_hash
from config import DEMO_ACCOUNTS
import os

# Opções válidas no sistema
TIPOS_OPERADOR = ("Policia", "Admin", "RH", "Supervisor")
TIPOS_REGISTO = ("Funcionario", "Estagiario", "Visitante")

# Porto estável do Supabase
DB_URL = "postgresql://postgres:Cessy.Maker1@db.inszsbbflhizvvqrxmpm.supabase.co:6543/postgres"

# --- CLASSES AUXILIARES PARA FAZER O SQLITE ACEITAR O CONTEXT MANAGER NO PYTHON 3.14 ---
class SQLiteCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()


class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn
        self.row_factory = conn.row_factory

    def cursor(self):
        # Em vez de modificar o cursor nativo, devolvemos o nosso embrulho seguro
        return SQLiteCursorWrapper(self.conn.cursor())

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def get_connection():
    """
    Conecta ao Supabase na nuvem ou ao SQLite local real dependendo do ambiente.
    """
    is_testing = os.environ.get("FLASK_ENV") == "testing" or os.environ.get("PYTEST_CURRENT_TEST") is not None

    if is_testing:
        conn = sqlite3.connect("banco_teste.db")
        conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        return SQLiteConnectionWrapper(conn)
    else:
        conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
        return conn

@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """
    Cria as tabelas na nuvem ou localmente ajustando a sintaxe para o banco ativo.
    """
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')

            # 1. Tabela de Operadores
            sql_operadores = """
            CREATE TABLE IF NOT EXISTS operadores (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                usuario TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                tipo TEXT NOT NULL,
                ativo INTEGER NOT NULL DEFAULT 1,
                criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
            if is_sqlite:
                sql_operadores = sql_operadores.replace("id SERIAL PRIMARY KEY", "id INTEGER PRIMARY KEY AUTOINCREMENT")
            cursor.execute(sql_operadores)

            # 2. Tabela de Registos de Acesso
            sql_registos = """
            CREATE TABLE IF NOT EXISTS registos_acesso (
                id SERIAL PRIMARY KEY,
                tipo TEXT NOT NULL,
                nome TEXT NOT NULL,
                tipo_documento TEXT NOT NULL DEFAULT 'BI',
                identificacao TEXT NOT NULL,
                contacto_visitante TEXT,
                contacto_visitado TEXT,
                eh_familiar INTEGER NOT NULL DEFAULT 0,
                departamento TEXT,
                motivo_visita TEXT,
                proveniencia TEXT,
                bens_declarados TEXT,
                valores_monetarios TEXT,
                seguranca_armas TEXT DEFAULT 'Nenhuma Arma Detetada',
                substancias_retidas TEXT,
                foto_documento TEXT, 
                funcionario_visitado TEXT,
                operador_id INTEGER NOT NULL,
                registrado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                saida_em TIMESTAMP,
                FOREIGN KEY (operador_id) REFERENCES operadores (id) ON DELETE CASCADE
            );
            """
            if is_sqlite:
                sql_registos = sql_registos.replace("id SERIAL PRIMARY KEY", "id INTEGER PRIMARY KEY AUTOINCREMENT")
            cursor.execute(sql_registos)

            # 3. Tabela de Logs
            sql_logs = """
            CREATE TABLE IF NOT EXISTS logs_operador (
                id SERIAL PRIMARY KEY,
                operador_id INTEGER,
                operador_nome TEXT,
                acao TEXT NOT NULL,
                detalhes TEXT,
                criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (operador_id) REFERENCES operadores (id) ON DELETE SET NULL
            );
            """
            if is_sqlite:
                sql_logs = sql_logs.replace("id SERIAL PRIMARY KEY", "id INTEGER PRIMARY KEY AUTOINCREMENT")
            cursor.execute(sql_logs)

        _seed_operadores(conn)

def _seed_operadores(conn):
    with conn.cursor() as cursor:
        is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
        
        for conta in DEMO_ACCOUNTS:
            sql_check = "SELECT 1 FROM operadores WHERE usuario = %s"
            sql_ins = "INSERT INTO operadores (nome, usuario, senha_hash, tipo) VALUES (%s, %s, %s, %s)"
            if is_sqlite:
                sql_check = sql_check.replace("%s", "?")
                sql_ins = sql_ins.replace("%s", "?")
                
            cursor.execute(sql_check, (conta["usuario"],))
            if not cursor.fetchone():
                cursor.execute(sql_ins, (conta["nome"], conta["usuario"], generate_password_hash(conta["senha"]), conta["tipo"]))

        sql_check_sup = "SELECT 1 FROM operadores WHERE usuario = %s"
        sql_ins_sup = "INSERT INTO operadores (nome, usuario, senha_hash, tipo) VALUES (%s, %s, %s, %s)"
        if is_sqlite:
            sql_check_sup = sql_check_sup.replace("%s", "?")
            sql_ins_sup = sql_ins_sup.replace("%s", "?")

        cursor.execute(sql_check_sup, ('supervisor',))
        if not cursor.fetchone():
            cursor.execute(sql_ins_sup, ('Supervisor STAE', 'supervisor', generate_password_hash('stae2026'), 'Supervisor'))

def get_operador_por_usuario(usuario):
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
            sql = "SELECT * FROM operadores WHERE usuario = %s AND ativo = 1"
            if is_sqlite:
                sql = sql.replace("%s", "?")
            cursor.execute(sql, (usuario,))
            row = cursor.fetchone()
            return dict(row) if row else None

def get_operador_por_id(operador_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
            sql = "SELECT * FROM operadores WHERE id = %s"
            if is_sqlite:
                sql = sql.replace("%s", "?")
            cursor.execute(sql, (operador_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

def listar_operadores():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nome, usuario, tipo, ativo, criado_em FROM operadores ORDER BY nome")
            rows = cursor.fetchall()
    return [dict(row) for row in rows]

def criar_operador(nome, usuario, senha, tipo):
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
            sql = "INSERT INTO operadores (nome, usuario, senha_hash, tipo) VALUES (%s, %s, %s, %s)"
            if is_sqlite:
                sql = sql.replace("%s", "?")
            cursor.execute(sql, (nome, usuario, generate_password_hash(senha), tipo))

def atualizar_operador(operador_id, nome, usuario, tipo, ativo):
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
            sql = "UPDATE operadores SET nome = %s, usuario = %s, tipo = %s, ativo = %s WHERE id = %s"
            if is_sqlite:
                sql = sql.replace("%s", "?")
            cursor.execute(sql, (nome, usuario, tipo, ativo, operador_id))

def alterar_senha_operador(operador_id, nova_senha):
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
            sql = "UPDATE operadores SET senha_hash = %s WHERE id = %s"
            if is_sqlite:
                sql = sql.replace("%s", "?")
            cursor.execute(sql, (generate_password_hash(nova_senha), operador_id))

def inserir_registo(dados):
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
            
            sql = """
            INSERT INTO registos_acesso (
                tipo, nome, tipo_documento, identificacao, contacto_visitante, contacto_visitado,
                departamento, motivo_visita, proveniencia, bens_declarados, valores_monetarios,
                seguranca_armas, substancias_retidas, foto_documento, eh_familiar, funcionario_visitado,
                operador_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            valores = (
                dados["tipo"], dados["nome"], dados.get("tipo_documento", "BI"), dados["identificacao"],
                dados.get("contacto_visitante"), dados.get("contacto_visitado"), dados.get("departamento"),
                dados.get("motivo_visita"), dados.get("proveniencia"), dados.get("bens_declarados"),
                dados.get("valores_monetarios"), dados.get("seguranca_armas", "Nenhuma Arma Detetada"),
                dados.get("substancias_retidas"), dados.get("foto_base64"), int(dados.get("eh_familiar", 0)),
                dados.get("funcionario_visitado"), dados["operador_id"]
            )

            if is_sqlite:
                sql = sql.replace("%s", "?")
                cursor.execute(sql, valores)
                return cursor.lastrowid
            else:
                sql += " RETURNING id"
                cursor.execute(sql, valores)
                return cursor.fetchone()["id"]

def registrar_saida(registo_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
            
            sql_select = "SELECT id, saida_em FROM registos_acesso WHERE id = %s"
            if is_sqlite:
                sql_select = sql_select.replace("%s", "?")
            cursor.execute(sql_select, (registo_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            if row["saida_em"]:
                return dict(row)
                
            sql_update = "UPDATE registos_acesso SET saida_em = CURRENT_TIMESTAMP WHERE id = %s"
            if is_sqlite:
                sql_update = sql_update.replace("%s", "?")
            cursor.execute(sql_update, (registo_id,))
            return get_registo_por_id(registo_id)

def get_registo_por_id(registo_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
            sql = """
            SELECT r.*, o.nome AS operador_nome, o.tipo AS operador_tipo
            FROM registos_acesso r
            JOIN operadores o ON o.id = r.operador_id
            WHERE r.id = %s
            """
            if is_sqlite:
                sql = sql.replace("%s", "?")
            cursor.execute(sql, (registo_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

def registrar_log(operador_id=None, operador_nome=None, acao="", detalhes=None):
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
            sql = "INSERT INTO logs_operador (operador_id, operador_nome, acao, detalhes) VALUES (%s, %s, %s, %s)"
            if is_sqlite:
                sql = sql.replace("%s", "?")
            cursor.execute(sql, (operador_id, operador_nome, acao, detalhes))

def _build_filtros_query(nome=None, data=None, tipo=None, apenas_dentro=False, is_sqlite=False):
    conditions = []
    params = []

    if nome:
        if is_sqlite:
            conditions.append("r.nome LIKE %s")
        else:
            conditions.append("r.nome ILIKE %s")
        params.append(f"%{nome}%")

    if data:
        if is_sqlite:
            conditions.append("date(r.registrado_em) = %s")
        else:
            conditions.append("r.registrado_em::date = %s::date")
        params.append(data)

    if tipo:
        conditions.append("r.tipo = %s")
        params.append(tipo)

    if apenas_dentro:
        conditions.append("r.saida_em IS NULL")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return where_clause, params

def contar_registos(nome=None, data=None, tipo=None, apenas_dentro=False):
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
            where_clause, params = _build_filtros_query(nome, data, tipo, apenas_dentro, is_sqlite=is_sqlite)
            query = f"SELECT COUNT(*) AS total FROM registos_acesso r {where_clause}"
            if is_sqlite:
                query = query.replace("%s", "?")
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row["total"]

def listar_registos(nome=None, data=None, tipo=None, limite=100, pagina=1, apenas_dentro=False):
    offset = max(pagina - 1, 0) * limite
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
            where_clause, params = _build_filtros_query(nome, data, tipo, apenas_dentro, is_sqlite=is_sqlite)
            query = f"""
                SELECT r.*, o.nome AS operador_nome, o.tipo AS operador_tipo
                FROM registos_acesso r
                JOIN operadores o ON o.id = r.operador_id
                {where_clause}
                ORDER BY r.registrado_em DESC
                LIMIT %s OFFSET %s
            """
            query_params = list(params) + [limite, offset]
            if is_sqlite:
                query = query.replace("%s", "?")
            cursor.execute(query, query_params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

def listar_todos_registos(nome=None, data=None, tipo=None, apenas_dentro=False):
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
            where_clause, params = _build_filtros_query(nome, data, tipo, apenas_dentro, is_sqlite=is_sqlite)
            query = f"""
                SELECT r.*, o.nome AS operador_nome, o.tipo AS operador_tipo
                FROM registos_acesso r
                JOIN operadores o ON o.id = r.operador_id
                {where_clause}
                ORDER BY r.registrado_em DESC
            """
            if is_sqlite:
                query = query.replace("%s", "?")
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

def listar_logs(limite=100, pagina=1):
    offset = max(pagina - 1, 0) * limite
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
            query = """
                SELECT * FROM logs_operador
                ORDER BY criado_em DESC
                LIMIT %s OFFSET %s
            """
            if is_sqlite:
                query = query.replace("%s", "?")
            cursor.execute(query, (limite, offset))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

def contar_logs():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM logs_operador")
            row = cursor.fetchone()
            return row["total"]

def obter_estatisticas_dashboard():
    with get_db() as conn:
        with conn.cursor() as cursor:
            is_sqlite = hasattr(conn, 'row_factory') and not hasattr(conn, 'cursor_factory')
            
            query_hoje = """
            SELECT
                COUNT(*) AS total_hoje,
                SUM(CASE WHEN tipo = 'Funcionario' THEN 1 ELSE 0 END) AS funcionarios_hoje,
                SUM(CASE WHEN tipo = 'Estagiario' THEN 1 ELSE 0 END) AS estagiarios_hoje,
                SUM(CASE WHEN tipo = 'Visitante' THEN 1 ELSE 0 END) AS visitantes_hoje,
                SUM(CASE WHEN saida_em IS NULL THEN 1 ELSE 0 END) AS dentro_agora
            FROM registos_acesso
            WHERE registrado_em::date = CURRENT_DATE;
            """
            if is_sqlite:
                query_hoje = query_hoje.replace(
                    "WHERE registrado_em::date = CURRENT_DATE;",
                    "WHERE date(registrado_em) = date('now', 'localtime');"
                )
            cursor.execute(query_hoje)
            hoje = cursor.fetchone()

            query_mes = """
            SELECT COUNT(*) AS total_mes
            FROM registos_acesso
            WHERE TO_CHAR(registrado_em, 'YYYY-MM') = TO_CHAR(CURRENT_DATE, 'YYYY-MM');
            """
            if is_sqlite:
                query_mes = query_mes.replace(
                    "WHERE TO_CHAR(registrado_em, 'YYYY-MM') = TO_CHAR(CURRENT_DATE, 'YYYY-MM');",
                    "WHERE strftime('%Y-%m', registrado_em) = strftime('%Y-%m', 'now', 'localtime');"
                )
            cursor.execute(query_mes)
            mes = cursor.fetchone()

            cursor.execute("SELECT COUNT(*) AS total FROM registos_acesso")
            total = cursor.fetchone()

    return {
        "total_hoje": hoje["total_hoje"] if hoje and hoje["total_hoje"] else 0,
        "funcionarios_hoje": hoje["funcionarios_hoje"] if hoje and hoje["funcionarios_hoje"] else 0,
        "estagiarios_hoje": hoje["estagiarios_hoje"] if hoje and hoje["estagiarios_hoje"] else 0,
        "visitantes_hoje": hoje["visitantes_hoje"] if hoje and hoje["visitantes_hoje"] else 0,
        "dentro_agora": hoje["dentro_agora"] if hoje and hoje["dentro_agora"] else 0,
        "total_mes": mes["total_mes"] if mes and mes["total_mes"] else 0,
        "total_geral": total["total"] if total and total["total"] else 0,
    }

def listar_registos_recentes(limite=20):
    return listar_registos(limite=limite)