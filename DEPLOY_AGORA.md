# PASSO A PASSO - Deploy Sistema STAE

## ASSUMINDO QUE VOCÊ JÁ TEM:
✅ Conta Supabase criada
✅ Conta Render criada
✅ Repositório GitHub criado

---

## PASSO 1: Supabase - Configurar Base de Dados

### 1.1 Executar Schema SQL
1. Aceda ao seu projeto Supabase
2. Clique em "SQL Editor" no menu lateral
3. Clique em "New query"
4. Abra o ficheiro `supabase_schema.sql` do projeto
5. Copie TODO o conteúdo
6. Cole no editor SQL do Supabase
7. Clique em "Run"
8. Verifique se apareceu "Success" (sem erros)

### 1.2 Obter DATABASE_URL
1. No Supabase, clique em "Settings" → "Database"
2. Procure a secção "Connection string"
3. Copie a string "URI" (começa com `postgresql://`)
4. **GUARDE ESTA STRING** - vai usar no Render

Exemplo: `postgresql://postgres:xyzabc@abcxyz.supabase.co:5432/postgres`

### 1.3 Criar Utilizadores
No mesmo SQL Editor do Supabase, execute este comando:

```sql
INSERT INTO operadores (nome, usuario, senha_hash, tipo) VALUES 
('Administrador STAE', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7xjZq5q6eO', 'Admin'),
('Operador Polícia', 'policia', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7xjZq5q6eO', 'Policia'),
('Operador RH', 'rh', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7xjZq5q6eO', 'RH'),
('Supervisor STAE', 'supervisor', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7xjZq5q6eO', 'Supervisor');
```

Clique "Run". Deve mostrar "Success".

---

## PASSO 2: GitHub - Atualizar Código

### 2.1 Fazer Push do Código
No terminal, na pasta do projeto:

```bash
git add .
git commit -m "Sistema STAE atualizado"
git push
```

Se der erro, primeiro:
```bash
git init
git add .
git commit -m "Sistema STAE pronto"
git branch -M main
git remote add origin URL_DO_SEU_REPOSITORIO_GITHUB
git push -u origin main
```

---

## PASSO 3: Render - Configurar e Deploy

### 3.1 Conectar Repositório
1. Aceda a https://dashboard.render.com
2. Clique em "New +" → "Web Service"
3. Clique em "Connect GitHub"
4. Autorize o Render a acessar seu GitHub
5. Selecione o repositório do projeto

### 3.2 Configurar Web Service
Preencha assim:

| Campo | Valor |
|-------|-------|
| Name | stae-sistema (ou outro nome) |
| Region | Frankfurt (ou mais próxima de Angola) |
| Branch | main |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python run.py` |

### 3.3 Configurar Variáveis de Ambiente
Clique em "Advanced" → "Add Environment Variable" e adicione estas 5:

| Key | Value |
|-----|-------|
| DATABASE_URL | (cole a string do PASSO 1.2) |
| STAE_SECRET_KEY | `stae-prod-2024-secure-key` |
| STAE_DEBUG | `false` |
| STAE_HOST | `0.0.0.0` |
| STAE_PORT | `5000` |

**IMPORTANTE**: A DATABASE_URL deve ser exatamente como copiou do Supabase.

### 3.4 Fazer Deploy
1. Clique em "Create Web Service"
2. Aguarde o build (aparece "Build in progress")
3. Se der erro, veja os logs abaixo
4. Quando aparecer "Deploy succeeded", está pronto!

---

## PASSO 4: Testar

### 4.1 Aceder ao Sistema
1. O Render vai mostrar a URL (ex: https://stae-sistema.onrender.com)
2. Clique na URL
3. Tente fazer login:
   - Utilizador: `admin`
   - Senha: `admin123`

### 4.2 Se Funcionar
✅ Deploy bem-sucedido!
✅ Sistema online e pronto para uso

### 4.3 Se Der Erro
1. No Render, clique em "Logs"
2. Veja o erro (geralmente em vermelho)
3. Partilhe o erro para eu corrigir

---

## ERROS COMUNS E SOLUÇÕES

### Erro: "Database connection failed"
**Causa**: DATABASE_URL incorreta
**Solução**: Verifique se copiou corretamente do Supabase

### Erro: "Module not found"
**Causa**: Falta dependência
**Solução**: Verifique se `requirements.txt` tem todas as dependências

### Erro: "Port already in use"
**Causa**: Conflito de porta
**Solução**: Render injeta porta automaticamente, não deve acontecer

### Erro: "Build failed"
**Causa**: Erro no código ou dependências
**Solução**: Verifique os logs de build

---

## RESUMO RÁPIDO

1. **Supabase**: Executar SQL → Copiar DATABASE_URL → Criar utilizadores
2. **GitHub**: Fazer push do código
3. **Render**: Conectar repo → Configurar variáveis → Deploy
4. **Testar**: Login com admin/admin123

**Tempo**: 10-15 minutos

---

## DEPOIS DO DEPLOY

- Sistema estará online na URL do Render
- Use o MANUAL_UTILIZADOR.md para orientar os operadores
- Para fazer alterações: push no GitHub → Render faz deploy automático
