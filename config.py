import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

FLASK_ENV = os.environ.get("FLASK_ENV", "development")
IS_PRODUCTION = FLASK_ENV == "production"

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise RuntimeError("Defina SECRET_KEY nas variaveis de ambiente antes do deploy.")
    SECRET_KEY = "dev-only-key-nao-usar-em-producao"

DEBUG = os.environ.get("FLASK_DEBUG", "0" if IS_PRODUCTION else "1") == "1"

# em producao cadastro publico fica desligado por padrao
ALLOW_REGISTRATION = os.environ.get("ALLOW_REGISTRATION", "0" if IS_PRODUCTION else "1") == "1"

# usuario inicial so no dev (ou se voce ligar explicitamente)
CREATE_DEFAULT_USER = os.environ.get("CREATE_DEFAULT_USER", "0" if IS_PRODUCTION else "1") == "1"

DEFAULT_USER = os.environ.get("DEFAULT_USER", "admin")
# em dev usa admin123 se nao passar nada; em prod exige senha forte via env
DEFAULT_PASS = os.environ.get("DEFAULT_PASS", "" if IS_PRODUCTION else "admin123")

DATABASE = BASE_DIR / "instance" / "app.db"
CSV_PATH = BASE_DIR / "data" / "vendas.csv"
SQL_INIT = BASE_DIR / "database" / "init_db.sql"

PORT = int(os.environ.get("PORT", 5000))
