import sqlite3
from datetime import datetime

import pandas as pd

from config import CSV_PATH, DATABASE, SQL_INIT


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    """roda o sql e importa csv na primeira vez"""
    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection()
    cur = conn.cursor()

    # executa script sql
    if SQL_INIT.exists():
        sql = SQL_INIT.read_text(encoding="utf-8")
        cur.executescript(sql)

    # verifica se ja tem dados
    count = cur.execute("SELECT COUNT(*) FROM vendas").fetchone()[0]
    if count == 0 and CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
        df.to_sql("vendas", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()


def load_vendas_df():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM vendas", conn)
    conn.close()

    if df.empty:
        return df

    df["data"] = pd.to_datetime(df["data"])
    df["receita"] = df["quantidade"] * df["valor_unitario"]
    df["custo_total"] = df["quantidade"] * df["custo_unitario"]
    df["lucro"] = df["receita"] - df["custo_total"]
    df["margem"] = (df["lucro"] / df["receita"].replace(0, 1)) * 100

    return df


def apply_filters(df, filtros):
    """aplica os filtros que vem do front"""
    if df.empty:
        return df

    out = df.copy()

    if filtros.get("data_inicio"):
        dt_ini = pd.to_datetime(filtros["data_inicio"])
        out = out[out["data"] >= dt_ini]

    if filtros.get("data_fim"):
        dt_fim = pd.to_datetime(filtros["data_fim"])
        out = out[out["data"] <= dt_fim]

    if filtros.get("regiao") and filtros["regiao"] != "todas":
        out = out[out["regiao"] == filtros["regiao"]]

    if filtros.get("categoria") and filtros["categoria"] != "todas":
        out = out[out["categoria"] == filtros["categoria"]]

    if filtros.get("status") and filtros["status"] != "todos":
        out = out[out["status"] == filtros["status"]]

    if filtros.get("vendedor") and filtros["vendedor"] != "todos":
        out = out[out["vendedor"] == filtros["vendedor"]]

    return out


def calc_kpis(df):
    if df.empty:
        return {
            "receita_total": 0,
            "lucro_total": 0,
            "margem_media": 0,
            "qtd_vendas": 0,
            "ticket_medio": 0,
            "taxa_conclusao": 0,
        }

    concluidos = df[df["status"] == "Concluído"]
    receita = float(df["receita"].sum())
    lucro = float(df["lucro"].sum())
    qtd = int(len(df))
    ticket = receita / qtd if qtd else 0
    margem = float(df["margem"].mean()) if qtd else 0

    taxa = 0
    if qtd > 0:
        taxa = (len(concluidos) / qtd) * 100

    return {
        "receita_total": round(receita, 2),
        "lucro_total": round(lucro, 2),
        "margem_media": round(margem, 1),
        "qtd_vendas": qtd,
        "ticket_medio": round(ticket, 2),
        "taxa_conclusao": round(taxa, 1),
    }


def chart_por_mes(df):
    if df.empty:
        return {"labels": [], "receita": [], "lucro": []}

    tmp = df.copy()
    tmp["mes"] = tmp["data"].dt.to_period("M").astype(str)
    grp = tmp.groupby("mes").agg({"receita": "sum", "lucro": "sum"}).reset_index()

    return {
        "labels": grp["mes"].tolist(),
        "receita": [round(x, 2) for x in grp["receita"].tolist()],
        "lucro": [round(x, 2) for x in grp["lucro"].tolist()],
    }


def chart_por_regiao(df):
    if df.empty:
        return {"labels": [], "valores": []}

    grp = df.groupby("regiao")["receita"].sum().sort_values(ascending=False)
    return {
        "labels": grp.index.tolist(),
        "valores": [round(v, 2) for v in grp.values.tolist()],
    }


def chart_por_categoria(df):
    if df.empty:
        return {"labels": [], "valores": []}

    grp = df.groupby("categoria")["receita"].sum().sort_values(ascending=False)
    return {
        "labels": grp.index.tolist(),
        "valores": [round(v, 2) for v in grp.values.tolist()],
    }


def chart_top_vendedores(df, top_n=5):
    if df.empty:
        return {"labels": [], "valores": []}

    grp = df.groupby("vendedor")["receita"].sum().sort_values(ascending=False).head(top_n)
    return {
        "labels": grp.index.tolist(),
        "valores": [round(v, 2) for v in grp.values.tolist()],
    }


def get_filter_options(df):
    if df.empty:
        return {
            "regioes": [],
            "categorias": [],
            "status_list": [],
            "vendedores": [],
            "data_min": "",
            "data_max": "",
        }

    return {
        "regioes": sorted(df["regiao"].dropna().unique().tolist()),
        "categorias": sorted(df["categoria"].dropna().unique().tolist()),
        "status_list": sorted(df["status"].dropna().unique().tolist()),
        "vendedores": sorted(df["vendedor"].dropna().unique().tolist()),
        "data_min": df["data"].min().strftime("%Y-%m-%d"),
        "data_max": df["data"].max().strftime("%Y-%m-%d"),
    }


def tabela_resumo(df, limit=15):
    if df.empty:
        return []

    cols = [
        "data", "regiao", "categoria", "produto",
        "vendedor", "quantidade", "receita", "lucro", "status"
    ]
    tmp = df[cols].copy()
    tmp["data"] = tmp["data"].dt.strftime("%d/%m/%Y")
    tmp["receita"] = tmp["receita"].round(2)
    tmp["lucro"] = tmp["lucro"].round(2)

    return tmp.head(limit).to_dict(orient="records")
