import pytest
import os

# 1. ATENÇÃO: Definimos o ambiente de teste antes de importar qualquer coisa da app
os.environ["FLASK_ENV"] = "testing"

from app import create_app
from app.database import init_db

@pytest.fixture(scope="session", autouse=True)
def preparar_banco_de_testes():
    """
    Esta fixture corre automaticamente uma vez antes de todos os testes começarem.
    Ela limpa resquícios antigos, cria o 'banco_teste.db' local e insere
    os operadores padrão (admin, policia, supervisor) necessários para o login.
    """
    # Se já existir um banco de testes antigo, remove para começar do zero
    if os.path.exists("banco_teste.db"):
        try:
            os.remove("banco_teste.db")
        except Exception:
            pass
            
    # Cria as tabelas e roda o seed de operadores na nossa base de dados local real
    init_db()
    
    yield  # Aqui é onde todos os teus testes abaixo vão rodar
    
    # Opcional: Remove o arquivo depois que todos os testes terminarem com sucesso
    if os.path.exists("banco_teste.db"):
        try:
            os.remove("banco_teste.db")
        except Exception:
            pass

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# --- OS TEUS TESTES ORIGINAIS (INTACTOS E SEM MOCKS!) ---

def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert "Login do Operador" in response.get_data(as_text=True)

def test_login_page_nao_mostra_contas_de_demonstracao(client):
    response = client.get("/login")
    html = response.get_data(as_text=True)
    assert "Contas de demonstração" not in html
    assert "admin123" not in html

def test_login_sucesso(client):
    # Agora vai ler "admin" e "admin123" diretamente do banco local gerado pelo init_db!
    response = client.post("/login", data={"usuario": "admin", "senha": "admin123"}, follow_redirects=True)
    assert response.status_code == 200
    assert "Menu de Registos" in response.get_data(as_text=True)

def test_login_falha(client):
    response = client.post("/login", data={"usuario": "admin", "senha": "errada"})
    assert response.status_code == 200
    assert "inválidos" in response.get_data(as_text=True)

def test_menu_requer_login(client):
    response = client.get("/menu", follow_redirects=True)
    assert "Login do Operador" in response.get_data(as_text=True)

def test_registar_visitante(client):
    client.post("/login", data={"usuario": "policia", "senha": "policia123"})
    response = client.post(
        "/registar/visitante",
        data={
            "nome": "João Teste",
            "identificacao": "BI123456",
            "eh_familiar": "nao",
            "motivo_visita": "Reunião",
            "departamento": "RH",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Visitante João Teste registado com sucesso." in response.get_data(as_text=True)
    assert "Comprovante" not in response.get_data(as_text=True)

def test_dashboard_admin(client):
    client.post("/login", data={"usuario": "admin", "senha": "admin123"})
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "Dashboard" in response.get_data(as_text=True)

def test_policia_nao_acessa_dashboard_ou_exporta(client):
    client.post("/login", data={"usuario": "policia", "senha": "policia123"})
    response = client.get("/dashboard", follow_redirects=True)
    assert response.status_code == 200
    assert "Não tem permissão" in response.get_data(as_text=True)

    response = client.get("/exportar_excel", follow_redirects=True)
    assert response.status_code == 200
    assert "Não tem permissão" in response.get_data(as_text=True)