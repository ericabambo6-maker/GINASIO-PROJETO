import base64
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from importlib import import_module

from werkzeug.security import generate_password_hash

from config import DATABASE_PATH, DEMO_ACCOUNTS, UPLOAD_DIR

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
create_client = None
try:
    create_client = import_module("supabase").create_client
except Exception:  # pragma: no cover - depende da instalação do pacote
    create_client = None

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
        return SQLiteCursorWrapper(self.conn.cursor())

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


class PostgresCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()


class PostgresConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn

    def cursor(self):
        return PostgresCursorWrapper(self.conn.cursor(cursor_factory=RealDictCursor))

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def _is_testing():
    return os.environ.get("FLASK_ENV") == "testing" or os.environ.get("PYTEST_CURRENT_TEST") is not None


def _is_supabase_backend():
    if _is_testing():
        return False
    backend = os.getenv("STAE_DB_BACKEND", "").strip().lower()
    if backend in {"supabase", "postgres", "postgresql"}:
        return True
    return bool(os.getenv("DATABASE_URL") or (os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY")))


def _resolve_db_url():
    direct_url = os.getenv("DATABASE_URL", "").strip()
    if direct_url:
        return direct_url
    explicit_sqlite = os.getenv("STAE_DB_URL", "").strip()
    if explicit_sqlite.startswith("sqlite"):
        return explicit_sqlite
    return explicit_sqlite


DB_URL = _resolve_db_url()


def _get_sqlite_path(url_or_path=None):
    candidate = url_or_path or os.environ.get("STAE_SQLITE_PATH", DATABASE_PATH)
    if candidate.startswith("sqlite:///"):
        candidate = candidate.replace("sqlite:///", "", 1)
    if candidate.startswith("sqlite://"):
        candidate = candidate.replace("sqlite://", "", 1)
    return candidate


def get_supabase_client():
    if create_client is None:
        return None
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


class Backend:
    def __init__(self):
        self.kind = "supabase" if _is_supabase_backend() else "sqlite"

    def get_connection(self):
        if self.kind == "supabase":
            if not PSYCOPG2_AVAILABLE:
                raise ImportError("psycopg2-binary is required for Supabase/PostgreSQL backend")
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise ValueError("DATABASE_URL environment variable is required for Supabase backend")
            conn = psycopg2.connect(db_url)
            return PostgresConnectionWrapper(conn)
        if _is_testing():
            conn = sqlite3.connect("banco_teste.db")
            conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
            conn.execute("PRAGMA foreign_keys = ON")
            return SQLiteConnectionWrapper(conn)

        sqlite_path = _get_sqlite_path(DB_URL if DB_URL and str(DB_URL).startswith("sqlite") else os.environ.get("STAE_SQLITE_PATH", DATABASE_PATH))
        sqlite_dir = os.path.dirname(sqlite_path) or "."
        os.makedirs(sqlite_dir, exist_ok=True)
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        conn.execute("PRAGMA foreign_keys = ON")
        return SQLiteConnectionWrapper(conn)

    @contextmanager
    def get_db(self):
        conn = self.get_connection()
        try:
            yield conn
            if conn is not None:
                conn.commit()
        except Exception as exc:
            if conn is not None:
                conn.rollback()
            raise exc
        finally:
            if conn is not None:
                conn.close()


BACKEND = Backend()


def get_connection():
    return BACKEND.get_connection()


@contextmanager
def get_db():
    with BACKEND.get_db() as conn:
        yield conn


def init_db():
    if BACKEND.kind == "supabase":
        # Supabase tables should be created via SQL editor or migration
        # We'll seed initial data if needed
        with BACKEND.get_db() as conn:
            with conn.cursor() as cursor:
                _seed_operadores_pg(cursor)
        return
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS operadores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    usuario TEXT NOT NULL UNIQUE,
                    senha_hash TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    ativo INTEGER NOT NULL DEFAULT 1,
                    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS registos_acesso (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS logs_operador (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operador_id INTEGER,
                    operador_nome TEXT,
                    acao TEXT NOT NULL,
                    detalhes TEXT,
                    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (operador_id) REFERENCES operadores (id) ON DELETE SET NULL
                )
                """
            )

        _seed_operadores(conn)


def _seed_operadores(conn):
    with conn.cursor() as cursor:
        for conta in DEMO_ACCOUNTS:
            cursor.execute("SELECT 1 FROM operadores WHERE usuario = ?", (conta["usuario"],))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO operadores (nome, usuario, senha_hash, tipo) VALUES (?, ?, ?, ?)",
                    (conta["nome"], conta["usuario"], generate_password_hash(conta["senha"]), conta["tipo"]),
                )
        cursor.execute("SELECT 1 FROM operadores WHERE usuario = ?", ("supervisor",))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO operadores (nome, usuario, senha_hash, tipo) VALUES (?, ?, ?, ?)",
                ("Supervisor STAE", "supervisor", generate_password_hash("stae2026"), "Supervisor"),
            )


def _seed_operadores_pg(cursor):
    for conta in DEMO_ACCOUNTS:
        cursor.execute("SELECT 1 FROM operadores WHERE usuario = %s", (conta["usuario"],))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO operadores (nome, usuario, senha_hash, tipo) VALUES (%s, %s, %s, %s)",
                (conta["nome"], conta["usuario"], generate_password_hash(conta["senha"]), conta["tipo"]),
            )
    cursor.execute("SELECT 1 FROM operadores WHERE usuario = %s", ("supervisor",))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO operadores (nome, usuario, senha_hash, tipo) VALUES (%s, %s, %s, %s)",
            ("Supervisor STAE", "supervisor", generate_password_hash("stae2026"), "Supervisor"),
        )




def get_operador_por_id(operador_id):
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            param = "?" if BACKEND.kind == "sqlite" else "%s"
            cursor.execute(f"SELECT * FROM operadores WHERE id = {param}", (operador_id,))
            row = cursor.fetchone()
            return dict(row) if row else None


def get_operador_por_usuario(usuario):
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            param = "?" if BACKEND.kind == "sqlite" else "%s"
            cursor.execute(f"SELECT * FROM operadores WHERE usuario = {param}", (usuario,))
            row = cursor.fetchone()
            return dict(row) if row else None

def registar_visitante_db(dados):
    client = get_supabase_client()
    if _is_supabase_backend() and client is not None:
        return client.table("visitantes").insert(dados).execute()
    return None


def listar_operadores():
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nome, usuario, tipo, ativo, criado_em FROM operadores ORDER BY nome")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]


def criar_operador(nome, usuario, senha, tipo):
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            param = "?" if BACKEND.kind == "sqlite" else "%s"
            cursor.execute(
                f"INSERT INTO operadores (nome, usuario, senha_hash, tipo) VALUES ({param}, {param}, {param}, {param})",
                (nome, usuario, generate_password_hash(senha), tipo),
            )


def atualizar_operador(operador_id, nome, usuario, tipo, ativo):
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            param = "?" if BACKEND.kind == "sqlite" else "%s"
            cursor.execute(
                f"UPDATE operadores SET nome = {param}, usuario = {param}, tipo = {param}, ativo = {param} WHERE id = {param}",
                (nome, usuario, tipo, ativo, operador_id),
            )


def alterar_senha_operador(operador_id, nova_senha):
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            param = "?" if BACKEND.kind == "sqlite" else "%s"
            cursor.execute(f"UPDATE operadores SET senha_hash = {param} WHERE id = {param}", (generate_password_hash(nova_senha), operador_id))


def _save_base64_image(base64_string, registo_id):
    """Save base64 image to file and return the file path."""
    if not base64_string:
        return None
    
    # Remove data URL prefix if present
    if base64_string.startswith("data:image"):
        base64_string = base64_string.split(",", 1)[1]
    
    # Decode base64
    image_data = base64.b64decode(base64_string)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"doc_{registo_id}_{timestamp}.jpg"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Save to file
    with open(filepath, "wb") as f:
        f.write(image_data)
    
    # Return relative path for database storage (without uploads/ prefix since route handles it)
    return f"documentos/{filename}"


def inserir_registo(dados):
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            try:
                param = "?" if BACKEND.kind == "sqlite" else "%s"
                params = "".join([f"{param}, " for _ in range(16)]) + param
                
                # First insert without photo to get the ID
                cursor.execute(
                    f"""
                    INSERT INTO registos_acesso (
                        tipo, nome, tipo_documento, identificacao, contacto_visitante, contacto_visitado,
                        departamento, motivo_visita, proveniencia, bens_declarados, valores_monetarios,
                        seguranca_armas, substancias_retidas, foto_documento, eh_familiar, funcionario_visitado,
                        operador_id
                    ) VALUES ({params})
                    """,
                    (
                        dados["tipo"],
                        dados["nome"],
                        dados.get("tipo_documento") or "BI",
                        dados["identificacao"],
                        dados.get("contacto_visitante"),
                        dados.get("contacto_visitado"),
                        dados.get("departamento"),
                        dados.get("motivo_visita"),
                        dados.get("proveniencia"),
                        dados.get("bens_declarados"),
                        dados.get("valores_monetarios"),
                        dados.get("seguranca_armas", "Nenhuma Arma Detetada"),
                        dados.get("substancias_retidas"),
                        None,  # Will be updated after getting ID
                        int(dados.get("eh_familiar", 0)),
                        dados.get("funcionario_visitado"),
                        dados["operador_id"],
                    ),
                )
                
                # Get the registo_id
                if BACKEND.kind == "sqlite":
                    registo_id = cursor.lastrowid
                else:
                    cursor.execute("SELECT lastval()")
                    registo_id = cursor.fetchone()["lastval"]
                
                # Save photo if provided
                foto_path = None
                if dados.get("foto_base64"):
                    foto_path = _save_base64_image(dados["foto_base64"], registo_id)
                
                # Update the record with photo path
                if foto_path:
                    cursor.execute(
                        f"UPDATE registos_acesso SET foto_documento = {param} WHERE id = {param}",
                        (foto_path, registo_id)
                    )
                
                print("Inserção realizada com sucesso!")
                return registo_id
            except Exception as e:
                print(f"ERRO AO INSERIR: {e}")
                raise e


def registrar_saida(registo_id):
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            param = "?" if BACKEND.kind == "sqlite" else "%s"
            cursor.execute(f"SELECT id, saida_em FROM registos_acesso WHERE id = {param}", (registo_id,))
            row = cursor.fetchone()
            if not row:
                return None
            if row["saida_em"]:
                return dict(row)
            cursor.execute(f"UPDATE registos_acesso SET saida_em = CURRENT_TIMESTAMP WHERE id = {param}", (registo_id,))
            return get_registo_por_id(registo_id)


def get_registo_por_id(registo_id):
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            param = "?" if BACKEND.kind == "sqlite" else "%s"
            cursor.execute(
                f"""
                SELECT r.*, o.nome AS operador_nome, o.tipo AS operador_tipo
                FROM registos_acesso r
                JOIN operadores o ON o.id = r.operador_id
                WHERE r.id = {param}
                """,
                (registo_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None


def registrar_log(operador_id=None, operador_nome=None, acao="", detalhes=None):
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            param = "?" if BACKEND.kind == "sqlite" else "%s"
            cursor.execute(
                f"INSERT INTO logs_operador (operador_id, operador_nome, acao, detalhes) VALUES ({param}, {param}, {param}, {param})",
                (operador_id, operador_nome, acao, detalhes),
            )


def _build_filtros_query(nome=None, data=None, tipo=None, apenas_dentro=False):
    conditions = []
    params = []
    param = "?" if BACKEND.kind == "sqlite" else "%s"
    if nome:
        conditions.append(f"r.nome LIKE {param}")
        params.append(f"%{nome}%")
    if data:
        if BACKEND.kind == "sqlite":
            conditions.append(f"date(r.registrado_em) = {param}")
        else:
            conditions.append(f"r.registrado_em::date = {param}")
        params.append(data)
    if tipo:
        conditions.append(f"r.tipo = {param}")
        params.append(tipo)
    if apenas_dentro:
        conditions.append("r.saida_em IS NULL")
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return where_clause, params


def contar_registos(nome=None, data=None, tipo=None, apenas_dentro=False):
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            where_clause, params = _build_filtros_query(nome, data, tipo, apenas_dentro)
            cursor.execute(f"SELECT COUNT(*) AS total FROM registos_acesso r {where_clause}", params)
            row = cursor.fetchone()
            return row["total"] if row else 0


def listar_registos(nome=None, data=None, tipo=None, limite=100, pagina=1, apenas_dentro=False):
    offset = max(pagina - 1, 0) * limite
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            where_clause, params = _build_filtros_query(nome, data, tipo, apenas_dentro)
            param = "?" if BACKEND.kind == "sqlite" else "%s"
            cursor.execute(
                f"""
                SELECT r.*, o.nome AS operador_nome, o.tipo AS operador_tipo
                FROM registos_acesso r
                JOIN operadores o ON o.id = r.operador_id
                {where_clause}
                ORDER BY r.registrado_em DESC
                LIMIT {param} OFFSET {param}
                """,
                params + [limite, offset],
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]


def listar_todos_registos(nome=None, data=None, tipo=None, apenas_dentro=False):
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            where_clause, params = _build_filtros_query(nome, data, tipo, apenas_dentro)
            cursor.execute(
                f"""
                SELECT r.*, o.nome AS operador_nome, o.tipo AS operador_tipo
                FROM registos_acesso r
                JOIN operadores o ON o.id = r.operador_id
                {where_clause}
                ORDER BY r.registrado_em DESC
                """,
                params,
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]


def listar_logs(limite=100, pagina=1):
    offset = max(pagina - 1, 0) * limite
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            param = "?" if BACKEND.kind == "sqlite" else "%s"
            cursor.execute(f"SELECT * FROM logs_operador ORDER BY criado_em DESC LIMIT {param} OFFSET {param}", (limite, offset))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]


def contar_logs():
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM logs_operador")
            row = cursor.fetchone()
            return row["total"] if row else 0


def obter_estatisticas_dashboard():
    with BACKEND.get_db() as conn:
        with conn.cursor() as cursor:
            if BACKEND.kind == "sqlite":
                query_hoje = """
                SELECT
                    COUNT(*) AS total_hoje,
                    SUM(CASE WHEN tipo = 'Funcionario' THEN 1 ELSE 0 END) AS funcionarios_hoje,
                    SUM(CASE WHEN tipo = 'Estagiario' THEN 1 ELSE 0 END) AS estagiarios_hoje,
                    SUM(CASE WHEN tipo = 'Visitante' THEN 1 ELSE 0 END) AS visitantes_hoje,
                    SUM(CASE WHEN saida_em IS NULL THEN 1 ELSE 0 END) AS dentro_agora
                FROM registos_acesso
                WHERE date(registrado_em) = date('now', 'localtime')
                """
                query_mes = """
                SELECT COUNT(*) AS total_mes
                FROM registos_acesso
                WHERE strftime('%Y-%m', registrado_em) = strftime('%Y-%m', 'now', 'localtime')
                """
            else:
                query_hoje = """
                SELECT
                    COUNT(*) AS total_hoje,
                    SUM(CASE WHEN tipo = 'Funcionario' THEN 1 ELSE 0 END) AS funcionarios_hoje,
                    SUM(CASE WHEN tipo = 'Estagiario' THEN 1 ELSE 0 END) AS estagiarios_hoje,
                    SUM(CASE WHEN tipo = 'Visitante' THEN 1 ELSE 0 END) AS visitantes_hoje,
                    SUM(CASE WHEN saida_em IS NULL THEN 1 ELSE 0 END) AS dentro_agora
                FROM registos_acesso
                WHERE registrado_em::date = CURRENT_DATE
                """
                query_mes = """
                SELECT COUNT(*) AS total_mes
                FROM registos_acesso
                WHERE TO_CHAR(registrado_em, 'YYYY-MM') = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
                """
            
            cursor.execute(query_hoje)
            hoje = cursor.fetchone()
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
