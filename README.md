# Dashboard Analítico de KPIs

Dashboard web para visualização de indicadores de desempenho a partir de dados CSV/SQL, com filtros dinâmicos, exportação em PDF e autenticação de usuários.

## Tecnologias

- **Python** + **Pandas** — tratamento e análise de dados
- **Flask** — backend e APIs REST
- **SQLite** — banco de dados (schema SQL + importação CSV)
- **Chart.js** — gráficos interativos no frontend
- **ReportLab** — geração de relatórios PDF

## Funcionalidades

- Login e cadastro de usuários
- KPIs: receita, lucro, margem, ticket médio, taxa de conclusão
- Gráficos: evolução mensal, receita por região/categoria, top vendedores
- Filtros dinâmicos por data, região, categoria, status e vendedor
- Exportação do relatório em PDF

## Como rodar

```bash
# clone o repo
git clone https://github.com/SEU_USUARIO/dashboard-kpis.git
cd dashboard-kpis

# ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# dependências
pip install -r requirements.txt

# iniciar
python app.py
```

Acesse: **http://localhost:5000**

**Login demo:** `admin` / `admin123`

## Estrutura do projeto

```
├── app.py                 # aplicação Flask
├── config.py              # configurações
├── data/vendas.csv        # dados de exemplo
├── database/init_db.sql   # schema SQL
├── utils/                 # auth, dados, PDF
├── templates/             # páginas HTML
└── static/                # CSS e JavaScript
```

## API

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/kpis` | Retorna KPIs, gráficos e tabela (aceita filtros via query string) |
| `GET /api/export/pdf` | Exporta relatório PDF com os filtros aplicados |

### Filtros disponíveis

`data_inicio`, `data_fim`, `regiao`, `categoria`, `status`, `vendedor`

## Trocar os dados

Edite `data/vendas.csv` e delete `instance/app.db` para forçar reimportação na próxima execução.

## Variáveis de ambiente (opcional)

```env
SECRET_KEY=sua-chave-secreta
DEFAULT_USER=admin
DEFAULT_PASS=admin123
PORT=5000
```
