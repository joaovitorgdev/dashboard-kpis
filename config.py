import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# chave pra sessao - em prod troca isso
SECRET_KEY = os.environ.get("SECRET_KEY", "kpi-dashboard-dev-key-2024")

DATABASE = BASE_DIR / "instance" / "app.db"
CSV_PATH = BASE_DIR / "data" / "vendas.csv"
SQL_INIT = BASE_DIR / "database" / "init_db.sql"

# usuario padrao so pra facilitar teste local
DEFAULT_USER = os.environ.get("DEFAULT_USER", "admin")
DEFAULT_PASS = os.environ.get("DEFAULT_PASS", "admin123")
