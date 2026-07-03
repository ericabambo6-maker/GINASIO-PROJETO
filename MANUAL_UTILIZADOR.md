# Manual de Utilizador - Sistema de Acesso STAE

## Índice
1. [Acesso ao Sistema](#1-acesso-ao-sistema)
2. [Tipos de Utilizadores](#2-tipos-de-utilizadores)
3. [Funcionalidades por Tipo](#3-funcionalidades-por-tipo)
4. [Registo de Visitantes](#4-registo-de-visitantes)
5. [Registo de Funcionários e Estagiários](#5-registo-de-funcionários-e-estagiários)
6. [Visualização de Registos](#6-visualização-de-registos)
7. [Exportação de Dados](#7-exportação-de-dados)
8. [Gestão de Operadores (Admin)](#8-gestão-de-operadores-admin)
9. [Alteração de Senha](#9-alteração-de-senha)
10. [Solução de Problemas](#10-solução-de-problemas)

---

## 1. Acesso ao Sistema

### 1.1 Login
1. Aceda à URL do sistema (ex: `https://stae-sistema.onrender.com`)
2. Introduza o **utilizador** e **senha**
3. Clique em "Entrar"

### 1.2 Credenciais Padrão

| Tipo | Utilizador | Senha |
|------|------------|-------|
| Admin | admin | admin123 |
| Policia | policia | policia123 |
| RH | rh | rh123 |
| Supervisor | supervisor | stae2026 |

⚠️ **Importante**: Altere a senha no primeiro acesso!

### 1.3 Logout
No canto superior direito, clique em "Sair"

---

## 2. Tipos de Utilizadores

### 2.1 Admin
- **Foco**: Gestão administrativa
- **Pode**: Ver registos, exportar dados, gerir operadores, ver logs, ver detalhes
- **Não pode**: Registrar entradas/saídas

### 2.2 Supervisor
- **Foco**: Supervisão e monitorização
- **Pode**: Ver registos, exportar dados, ver logs, ver detalhes
- **Não pode**: Registrar entradas/saídas, gerir operadores

### 2.3 Policia
- **Foco**: Controlo de visitantes
- **Pode**: Registrar visitantes, registrar saídas
- **Não pode**: Registrar funcionários/estagiários, ver detalhes

### 2.4 RH
- **Foco**: Gestão de funcionários
- **Pode**: Registrar funcionários e estagiários
- **Não pode**: Registrar visitantes, ver detalhes

---

## 3. Funcionalidades por Tipo

### 3.1 Admin
No menu principal, o Admin vê:
- **Dashboard**: Estatísticas do sistema
- **Gestão de Operadores**: Criar/editar/apagar utilizadores
- **Logs do Sistema**: Histórico de ações
- **Registos de Acesso**: Lista de todas as entradas/saídas

### 3.2 Supervisor
No menu principal, o Supervisor vê:
- **Dashboard**: Estatísticas do sistema
- **Gestão de Operadores**: Ver utilizadores
- **Logs do Sistema**: Histórico de ações
- **Registos de Acesso**: Lista de todas as entradas/saídas

### 3.3 Policia
No menu principal, a Polícia vê:
- **Visitante**: Formulário para registrar visitantes
- **Registos de Acesso**: Lista de entradas/saídas

### 3.4 RH
No menu principal, o RH vê:
- **Funcionário**: Formulário para registrar funcionários
- **Estagiário**: Formulário para registrar estagiários
- **Registos de Acesso**: Lista de entradas/saídas

---

## 4. Registo de Visitantes

### 4.1 Acesso
Apenas **Policia** pode registrar visitantes.

### 4.2 Preenchimento do Formulário

#### Passo 1: Dados Básicos
1. **Nome**: Nome completo do visitante
2. **Tipo de Documento**: Selecionar "BI" ou "Passaporte"
3. **Número do Documento**: Introduzir o número
   - ✨ **Autocomplete**: Se o visitante já foi registrado antes, o sistema sugere os dados automaticamente após digitar 3 caracteres

#### Passo 2: Foto do Documento
1. Clique em "Iniciar Câmera"
2. Permita o acesso à câmera do dispositivo
3. Posicione o documento à frente da câmera
4. Clique em "Capturar Foto"
5. Se necessário, clique em "Tirar Novamente"

#### Passo 3: Tipo de Visita
Selecione se é familiar de funcionário:
- **Sim**: Preencher o nome do funcionário visitado
- **Não**: Preencher motivo e departamento

#### Passo 4: Informações Adicionais (não familiar)
- **Proveniência**: Empresa ou entidade de origem
- **Contacto do Visitante**: Telefone ou email
- **Contacto do Funcionário Visitado**: Telefone ou email
- **Funcionário Visitado**: Primeiro nome e apelido
- **Declaração de Bens**: Tipo e valor (ex: Laptop, Telemóvel)
- **Valores Monetários**: Ex: 5000 AOA
- **Segurança - Armas Detetadas**: Selecionar se aplicável
- **Substâncias Retidas**: Ex: Nenhuma

#### Passo 5: Confirmar
Clique em "Registar Visitante"

### 4.3 Registrar Saída
1. Na lista de registos, localize o visitante
2. Clique no botão "Saída" na coluna Ações
3. A saída é registrada automaticamente

---

## 5. Registo de Funcionários e Estagiários

### 5.1 Acesso
Apenas **RH** pode registrar funcionários e estagiários.

### 5.2 Registo de Funcionário
1. Preencha **Nome**
2. Preencha **Nº de identificação** (cartão)
3. Preencha **Departamento**
4. Clique em "Registar Entrada"

### 5.3 Registo de Estagiário
1. Preencha **Nome**
2. Preencha **Nº de identificação** (cartão)
3. Preencha **Departamento**
4. Clique em "Registar Entrada"

### 5.4 Registrar Saída
1. Na lista de registos, localize o funcionário/estagiário
2. Clique no botão "Saída" na coluna Ações

---

## 6. Visualização de Registos

### 6.1 Acesso à Lista
Todos os utilizadores podem ver a lista de registos de acesso.

### 6.2 Filtros
- **Nome**: Filtrar por nome
- **Data**: Filtrar por data específica
- **Tipo**: Filtrar por tipo (Funcionário, Estagiário, Visitante)
- **Apenas Dentro**: Mostrar apenas pessoas dentro do edifício

### 6.3 Detalhes do Registo (Modal)
Apenas **Admin** e **Supervisor** podem ver detalhes completos.

Para ver detalhes:
1. Clique na linha do registo na tabela
2. Um modal abre com todas as informações:
   - Foto do documento (se disponível)
   - Todos os dados do registo
   - Informações do operador que registou

### 6.4 Informações na Tabela
- **Entrada**: Data e hora de entrada
- **Saída**: Data e hora de saída (ou "—" se ainda dentro)
- **Tipo**: Funcionário, Estagiário ou Visitante
- **Nome**: Nome da pessoa
- **Identificação**: Nº de documento
- **Detalhes**: Departamento/motivo
- **Operador**: Nome do operador que registou
- **Ações**: Botão "Saída" (se aplicável)

---

## 7. Exportação de Dados

### 7.1 Acesso
**Admin**, **Supervisor** e **Policia** podem exportar dados.

### 7.2 Como Exportar
1. Aplique os filtros desejados
2. Clique em "Exportar Excel"
3. O ficheiro Excel é descarregado automaticamente

### 7.3 Conteúdo do Excel
- Todos os registos visíveis na tabela
- Inclui todos os campos e detalhes

---

## 8. Gestão de Operadores (Admin)

### 8.1 Acesso
Apenas **Admin** pode gerir operadores.

### 8.2 Criar Operador
1. Clique em "Gestão de Operadores"
2. Clique em "Adicionar Operador"
3. Preencha:
   - **Nome**
   - **Utilizador** (único)
   - **Senha**
   - **Tipo** (Admin, Supervisor, RH, Policia)
4. Clique em "Salvar"

### 8.3 Editar Operador
1. Clique em "Editar" ao lado do operador
2. Modifique os dados necessários
3. Clique em "Salvar"

### 8.4 Desativar Operador
1. Clique em "Desativar" ao lado do operador
2. Confirme a ação
3. O operador não pode mais fazer login

### 8.5 Tipos de Operadores
- **Admin**: Acesso total administrativo
- **Supervisor**: Visualização e monitorização
- **RH**: Gestão de funcionários
- **Policia**: Controlo de visitantes

---

## 9. Alteração de Senha

### 9.1 Como Alterar
1. No menu superior, clique em "Senha"
2. Introduza a **senha atual**
3. Introduza a **nova senha**
4. Confirme a **nova senha**
5. Clique em "Alterar"

### 9.2 Requisitos
- A senha atual deve estar correta
- A nova senha deve ter pelo menos 6 caracteres

---

## 10. Solução de Problemas

### 10.1 Não consigo fazer login
**Possíveis causas:**
- Utilizador ou senha incorretos
- Conta desativada
- Sistema em manutenção

**Soluções:**
- Verifique credenciais
- Contacte o Admin
- Tente novamente mais tarde

### 10.2 A câmera não funciona
**Possíveis causas:**
- Permissão de câmera negada
- Dispositivo sem câmera
- Navegador incompatível

**Soluções:**
- Permita acesso à câmera
- Use dispositivo com câmera
- Tente Chrome ou Firefox

### 10.3 Autocomplete não funciona
**Possíveis causas:**
- Visitante nunca registrado antes
- Menos de 3 caracteres digitados

**Soluções:**
- Digite pelo menos 3 caracteres
- Preencha manualmente se for novo visitante

### 10.4 Foto não aparece no modal
**Possíveis causas:**
- Registo antigo (sem foto)
- Erro ao salvar foto

**Soluções:**
- Registos antigos não têm foto
- Novos registos devem ter foto

### 10.5 Exportação não funciona
**Possíveis causas:**
- Sem filtros aplicados
- Erro de conexão

**Soluções:**
- Aplique filtros antes de exportar
- Tente novamente

### 10.6 Sistema lento
**Possíveis causas:**
- Muitos registos
- Conexão lenta

**Soluções:**
- Use filtros para reduzir resultados
- Verifique conexão de internet

---

## 11. Boas Práticas

### 11.1 Para Operadores
- Sempre registre entrada e saída
- Verifique dados antes de confirmar
- Use autocomplete para visitantes recorrentes
- Capture foto do documento sempre que possível

### 11.2 Para Admin
- Revise logs regularmente
- Mantenha operadores atualizados
- Faça backup regularmente
- Monitore uso do sistema

### 11.3 Para Todos
- Altere senha regularmente
- Não partilhe credenciais
- Reporte problemas imediatamente
- Mantenha dados atualizados

---

## 12. Suporte

Para problemas ou dúvidas:
- Contacte o administrador do sistema
- Verifique este manual
- Consulte os logs do sistema (Admin/Supervisor)

---

**Versão**: 1.0  
**Data**: Julho 2026  
**Sistema**: STAE - Controlo de Acessos
