import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


PDF_DIR = os.getenv("PDF_DIRECTORY", "output/pdf")


def _safe(value) -> str:
    return str(value or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_pdf(person: dict, output_path: str | None = None) -> str:
    os.makedirs(PDF_DIR, exist_ok=True)
    output_path = output_path or os.path.join(PDF_DIR, f"ficha_{person['id']}.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="Ficha de Cadastro",
        author="Vanda Silva",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleCustom", parent=styles["Title"], alignment=TA_CENTER,
        fontName="Helvetica-Bold", fontSize=23, leading=28, textColor=colors.HexColor("#173B65")
    )
    label = ParagraphStyle(
        "Label", parent=styles["BodyText"], fontName="Helvetica-Bold",
        fontSize=10, leading=13, textColor=colors.HexColor("#173B65")
    )
    value = ParagraphStyle(
        "Value", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=11, leading=14, textColor=colors.HexColor("#202020")
    )
    small = ParagraphStyle(
        "Small", parent=styles["BodyText"], fontSize=8.5, leading=11,
        textColor=colors.HexColor("#555555")
    )

    def cell(lbl, val):
        return [Paragraph(lbl, label), Spacer(1, 1.5 * mm), Paragraph(_safe(val), value)]

    story = [
        Paragraph("FICHA DE CADASTRO", title),
        Spacer(1, 5 * mm),
        Table(
            [[Paragraph(f"<b>INDICADO POR:</b> {_safe(person.get('indicador_nome', 'Vanda Silva'))}", value)]],
            colWidths=[170 * mm],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF2FA")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#8AA9C7")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B6CADC")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]),
        ),
        Spacer(1, 5 * mm),
    ]

    rows = [
        [cell("NOME COMPLETO", person.get("nome")), ""],
        [cell("Nº DO TÍTULO", person.get("titulo")), cell("ZONA / SEÇÃO", f"{person.get('zona', '')} / {person.get('secao', '')}")],
        [cell("ENDEREÇO COMPLETO", person.get("endereco")), ""],
        [cell("DATA DE NASCIMENTO", person.get("nascimento")), cell("CPF", person.get("cpf"))],
        [cell("Nº CELULAR", person.get("celular")), ""],
    ]
    table = Table(rows, colWidths=[110 * mm, 60 * mm], rowHeights=[22 * mm, 22 * mm, 29 * mm, 22 * mm, 22 * mm])
    table.setStyle(TableStyle([
        ("SPAN", (0, 0), (1, 0)),
        ("SPAN", (0, 2), (1, 2)),
        ("SPAN", (0, 4), (1, 4)),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#173B65")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#A9B7C5")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([
        table,
        Spacer(1, 7 * mm),
        Paragraph("Cadastro enviado pelo WhatsApp com autorização para uso dos dados em cadastro, contato e relatórios internos.", small),
        Spacer(1, 2 * mm),
        Paragraph(f"Código de indicação: {_safe(person.get('codigo_proprio', 'MODELO'))} | Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", small),
    ])
    doc.build(story)
    return output_path
