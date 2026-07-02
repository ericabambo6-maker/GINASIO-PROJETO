-- Schema para Supabase - Sistema de Acesso STAE

-- Tabela de operadores
CREATE TABLE IF NOT EXISTS operadores (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    usuario TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('Policia', 'Admin', 'RH', 'Supervisor')),
    ativo INTEGER NOT NULL DEFAULT 1,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de registos de acesso
CREATE TABLE IF NOT EXISTS registos_acesso (
    id SERIAL PRIMARY KEY,
    tipo TEXT NOT NULL CHECK (tipo IN ('Funcionario', 'Estagiario', 'Visitante')),
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
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operador_id) REFERENCES operadores (id) ON DELETE CASCADE
);

-- Tabela de logs de operador
CREATE TABLE IF NOT EXISTS logs_operador (
    id SERIAL PRIMARY KEY,
    operador_id INTEGER,
    operador_nome TEXT,
    acao TEXT NOT NULL,
    detalhes TEXT,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operador_id) REFERENCES operadores (id) ON DELETE SET NULL
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_registos_operador ON registos_acesso(operador_id);
CREATE INDEX IF NOT EXISTS idx_registos_data ON registos_acesso(registrado_em);
CREATE INDEX IF NOT EXISTS idx_registos_saida ON registos_acesso(saida_em);
CREATE INDEX IF NOT EXISTS idx_logs_operador ON logs_operador(operador_id);
CREATE INDEX IF NOT EXISTS idx_logs_data ON logs_operador(criado_em);
