import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def gerar_pdf(kpis, tabela, filtros_usados):
    """monta um pdf simples com os kpis e tabela"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        "titulo",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
    )
    sub_style = styles["Normal"]

    elementos = []

    elementos.append(Paragraph("Relatório de KPIs — Dashboard Analítico", titulo_style))
    elementos.append(Paragraph(
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        sub_style,
    ))
    elementos.append(Spacer(1, 0.5 * cm))

    # filtros aplicados
    filtros_txt = []
    for k, v in filtros_usados.items():
        if v and v not in ("todas", "todos", ""):
            filtros_txt.append(f"{k}: {v}")

    if filtros_txt:
        elementos.append(Paragraph("Filtros: " + " | ".join(filtros_txt), sub_style))
        elementos.append(Spacer(1, 0.3 * cm))

    # tabela de kpis
    kpi_data = [
        ["Indicador", "Valor"],
        ["Receita Total", f"R$ {kpis['receita_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
        ["Lucro Total", f"R$ {kpis['lucro_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
        ["Margem Média", f"{kpis['margem_media']}%"],
        ["Qtd. Vendas", str(kpis["qtd_vendas"])],
        ["Ticket Médio", f"R$ {kpis['ticket_medio']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
        ["Taxa Conclusão", f"{kpis['taxa_conclusao']}%"],
    ]

    t_kpi = Table(kpi_data, colWidths=[8 * cm, 8 * cm])
    t_kpi.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    elementos.append(t_kpi)
    elementos.append(Spacer(1, 0.8 * cm))

    elementos.append(Paragraph("Últimas vendas (amostra)", styles["Heading2"]))
    elementos.append(Spacer(1, 0.2 * cm))

    if tabela:
        headers = ["Data", "Região", "Categoria", "Produto", "Receita", "Status"]
        rows = [headers]
        for row in tabela[:12]:
            rows.append([
                row.get("data", ""),
                row.get("regiao", ""),
                row.get("categoria", ""),
                row.get("produto", "")[:20],
                f"R$ {row.get('receita', 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                row.get("status", ""),
            ])

        t_vendas = Table(rows, repeatRows=1)
        t_vendas.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d6a4f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        elementos.append(t_vendas)
    else:
        elementos.append(Paragraph("Nenhum dado encontrado com os filtros atuais.", sub_style))

    doc.build(elementos)
    buffer.seek(0)
    return buffer
