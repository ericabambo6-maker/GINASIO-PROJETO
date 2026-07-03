# Checklist de Deploy - Sistema STAE

## PASSO 1: Supabase (Base de Dados)

### 1.1 Criar Projeto
1. Aceda a https://supabase.com
2. Login → "New Project"
3. Name: `stae-sistema`
4. Database Password: (guarde!)
5. Region: South Africa (ou mais próxima)
6. Clique "Create new project"
7. Aguarde 2-3 minutos

### 1.2 Criar Tabelas
1. No Supabase → "SQL Editor"
2. "New query"
3. Copie TODO o conteúdo de `supabase_schema.sql`
4. Cole e clique "Run"

### 1.3 Obter DATABASE_URL
1. Supabase → "Settings" → "Database"
2. Copie "Connection string" → "URI"
3. Formato: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`
4. **GUARDE ESTA STRING**

### 1.4 Criar Utilizadores
No SQL Editor, execute:

```sql
INSERT INTO operadores (nome, usuario, senha_hash, tipo) VALUES 
('Administrador STAE', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7xjZq5q6eO', 'Admin'),
('Operador Polícia', 'policia', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7xjZq5q6eO', 'Policia'),
('Operador RH', 'rh', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7xjZq5q6eO', 'RH'),
('Supervisor STAE', 'supervisor', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7xjZq5q6eO', 'Supervisor');
```

**Senhas**: admin123, policia123, rh123, stae2026

---

## PASSO 2: GitHub

### 2.1 Criar Repositório
1. Aceda a https://github.com
2. "New repository"
3. Name: `ginasio-projeto`
4. "Create repository"

### 2.2 Fazer Push
No terminal, na pasta do projeto:

```bash
git init
git add .
git commit -m "Sistema STAE pronto para produção"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/ginasio-projeto.git
git push -u origin main
```

---

## PASSO 3: Render (Deploy)

### 3.1 Criar Web Service
1. Aceda a https://dashboard.render.com
2. "New +" → "Web Service"
3. "Connect GitHub"
4. Selecione `ginasio-projeto`
5. Configure:

| Campo | Valor |
|-------|-------|
| Name | stae-sistema |
| Region | Frankfurt (ou mais próxima) |
| Branch | main |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python run.py` |

### 3.2 Variáveis de Ambiente
Clique "Advanced" → "Add Environment Variable":

| Key | Value |
|-----|-------|
| DATABASE_URL | (string do passo 1.3) |
| STAE_SECRET_KEY | `stae-prod-2024-secure-key` |
| STAE_DEBUG | `false` |
| STAE_HOST | `0.0.0.0` |
| STAE_PORT | `5000` |

### 3.3 Deploy
1. Clique "Create Web Service"
2. Aguarde 3-5 minutos
3. Sistema estará em: `https://stae-sistema.onrender.com`

---

## PASSO 4: Testes

### 4.1 Login
1. Aceda à URL do Render
2. Login: `admin` / `admin123`
3. Se funcionar → deploy OK!

### 4.2 Testar Funcionalidades
- Registrar visitante
- Ver lista de registos
- Ver modal de detalhes
- Testar outros utilizadores

---

## IMPORTANTE: Fotos

⚠️ **Render Free não guarda ficheiros entre deploys**

Para produção, precisará de:
1. Supabase Storage (ou serviço similar)
2. Modificar código para usar storage externo

**Para demonstração/venda**: O sistema funciona, mas fotos podem ser perdidas ao fazer novo deploy.

---

## Resumo

✅ Supabase: Criar projeto, executar SQL, obter DATABASE_URL  
✅ GitHub: Fazer push do código  
✅ Render: Criar web service, configurar variáveis, deploy  
✅ Testar: Login e funcionalidades básicas

**Tempo estimado**: 15-20 minutos
