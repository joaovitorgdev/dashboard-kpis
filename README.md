# Dashboard Analítico de KPIs

Dashboard web para visualização de indicadores de desempenho a partir de dados CSV/SQL, com filtros dinâmicos, exportação em PDF e autenticação de usuários.

## Tecnologias

- **Python** + **Pandas** — tratamento e análise de dados
- **Flask** — backend e APIs REST
- **SQLite** — banco de dados (schema SQL + importação CSV)
- **Chart.js** — gráficos interativos no frontend
- **ReportLab** — geração de relatórios PDF

## Funcionalidades

- Login de usuários (cadastro opcional)
- KPIs: receita, lucro, margem, ticket médio, taxa de conclusão
- Gráficos: evolução mensal, receita por região/categoria, top vendedores
- Filtros dinâmicos por data, região, categoria, status e vendedor
- Exportação do relatório em PDF

## Desenvolvimento local

```bash
git clone https://github.com/joaovitorgdev/dashboard-kpis.git
cd dashboard-kpis

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

# copie e ajuste se quiser
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/Mac

python app.py
```

Acesse: **http://localhost:5000**

No modo desenvolvimento, o cadastro fica aberto e um usuário inicial é criado automaticamente (veja `.env.example`).

## Deploy em produção

### Variáveis obrigatórias

| Variável | Valor recomendado |
|----------|-------------------|
| `FLASK_ENV` | `production` |
| `FLASK_DEBUG` | `0` |
| `SECRET_KEY` | chave aleatória longa |
| `DEFAULT_USER` | seu usuário admin |
| `DEFAULT_PASS` | senha forte (só na 1ª subida) |
| `ALLOW_REGISTRATION` | `0` |
| `CREATE_DEFAULT_USER` | `1` na 1ª subida, depois `0` |

Gere uma chave segura:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Render / Railway

1. Conecte o repositório GitHub
2. Build: `pip install -r requirements.txt -r requirements-prod.txt`
3. Start: `gunicorn app:app --bind 0.0.0.0:$PORT` (ou use o `Procfile`)
4. Configure as variáveis de ambiente acima
5. Após o primeiro login, defina `CREATE_DEFAULT_USER=0` para não recriar admin

### Segurança em produção

- Cadastro público desligado por padrão
- `debug` desligado
- Cookies de sessão com `Secure` e `HttpOnly`
- Sem credenciais demo na interface
- `SECRET_KEY` obrigatória — app não sobe sem ela

## Estrutura do projeto

```
├── app.py
├── config.py
├── .env.example
├── Procfile
├── data/vendas.csv
├── database/init_db.sql
├── utils/
├── templates/
└── static/
```

## API

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/kpis` | KPIs, gráficos e tabela (filtros via query string) |
| `GET /api/export/pdf` | Exporta relatório PDF |

Filtros: `data_inicio`, `data_fim`, `regiao`, `categoria`, `status`, `vendedor`

## Trocar os dados

Edite `data/vendas.csv` e delete `instance/app.db` para reimportar na próxima execução.
