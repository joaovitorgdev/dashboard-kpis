-- schema basico pro dashboard
-- roda na inicializacao do app

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    regiao TEXT,
    categoria TEXT,
    produto TEXT,
    vendedor TEXT,
    quantidade INTEGER,
    valor_unitario REAL,
    custo_unitario REAL,
    status TEXT
);

CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data);
CREATE INDEX IF NOT EXISTS idx_vendas_regiao ON vendas(regiao);
CREATE INDEX IF NOT EXISTS idx_vendas_categoria ON vendas(categoria);
