import sqlite3
from functools import wraps

from flask import redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from config import DATABASE, DEFAULT_PASS, DEFAULT_USER


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_users():
    """cria tabela e usuario padrao se nao existir"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # garante admin pra primeiro acesso
    row = cur.execute("SELECT id FROM users WHERE username = ?", (DEFAULT_USER,)).fetchone()
    if not row:
        pwd = generate_password_hash(DEFAULT_PASS)
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (DEFAULT_USER, pwd),
        )

    conn.commit()
    conn.close()


def register_user(username, password):
    if not username or not password:
        return False, "Preencha usuario e senha."

    if len(password) < 6:
        return False, "Senha precisa ter pelo menos 6 caracteres."

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        conn.commit()
        return True, "Conta criada!"
    except sqlite3.IntegrityError:
        return False, "Usuario ja existe."
    finally:
        conn.close()


def verify_user(username, password):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user["password_hash"], password):
        return dict(user)
    return None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated
