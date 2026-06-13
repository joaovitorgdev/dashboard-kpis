import os
from datetime import datetime

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

load_dotenv()

from config import ALLOW_REGISTRATION, DEBUG, IS_PRODUCTION, PORT, SECRET_KEY
from utils.auth import init_users, login_required, register_user, verify_user
from utils.data_loader import (
    apply_filters,
    calc_kpis,
    chart_por_categoria,
    chart_por_mes,
    chart_por_regiao,
    chart_top_vendedores,
    get_filter_options,
    load_vendas_df,
    setup_database,
    tabela_resumo,
)
from utils.pdf_export import gerar_pdf

app = Flask(__name__)
app.secret_key = SECRET_KEY

# cookies de sessao mais seguros fora do debug
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
if IS_PRODUCTION:
    app.config["SESSION_COOKIE_SECURE"] = True


@app.before_request
def init_app():
    if not getattr(app, "_db_ready", False):
        setup_database()
        init_users()
        app._db_ready = True


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = verify_user(username, password)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session.permanent = True
            flash("Login ok!", "success")
            return redirect(url_for("dashboard"))

        flash("Usuario ou senha invalidos.", "error")

    return render_template("login.html", allow_registration=ALLOW_REGISTRATION)


@app.route("/register", methods=["GET", "POST"])
def register():
    if not ALLOW_REGISTRATION:
        flash("Cadastro desabilitado.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        ok, msg = register_user(username, password)
        flash(msg, "success" if ok else "error")
        if ok:
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Voce saiu.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    df = load_vendas_df()
    opcoes = get_filter_options(df)
    return render_template(
        "dashboard.html",
        username=session.get("username"),
        opcoes=opcoes,
    )


def _pegar_filtros():
    return {
        "data_inicio": request.args.get("data_inicio", ""),
        "data_fim": request.args.get("data_fim", ""),
        "regiao": request.args.get("regiao", "todas"),
        "categoria": request.args.get("categoria", "todas"),
        "status": request.args.get("status", "todos"),
        "vendedor": request.args.get("vendedor", "todos"),
    }


@app.route("/api/kpis")
@login_required
def api_kpis():
    df = load_vendas_df()
    filtros = _pegar_filtros()
    filtrado = apply_filters(df, filtros)

    payload = {
        "kpis": calc_kpis(filtrado),
        "charts": {
            "mes": chart_por_mes(filtrado),
            "regiao": chart_por_regiao(filtrado),
            "categoria": chart_por_categoria(filtrado),
            "vendedores": chart_top_vendedores(filtrado),
        },
        "tabela": tabela_resumo(filtrado),
        "filtros": filtros,
        "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }

    return jsonify(payload)


@app.route("/api/export/pdf")
@login_required
def export_pdf():
    df = load_vendas_df()
    filtros = _pegar_filtros()
    filtrado = apply_filters(df, filtros)
    kpis = calc_kpis(filtrado)
    tabela = tabela_resumo(filtrado, limit=20)

    pdf_buffer = gerar_pdf(kpis, tabela, filtros)

    nome = f"relatorio_kpis_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=nome,
    )


if __name__ == "__main__":
    app.run(debug=DEBUG, host="0.0.0.0", port=PORT)
