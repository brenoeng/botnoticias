from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from datetime import datetime
from collections import defaultdict


def gerar_pdf(noticias, nome_arquivo="noticias.pdf", categoria=None):
    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Title'], fontName="Helvetica-Bold", fontSize=22, spaceAfter=20, alignment=1)
    subtitle_style = ParagraphStyle(
        'SubtitleStyle', parent=styles['Normal'], fontName="Helvetica-Bold", fontSize=12, spaceAfter=30, alignment=1)
    section_style = ParagraphStyle(
        'SectionStyle', parent=styles['Heading1'], fontName="Helvetica-Bold", fontSize=16, spaceBefore=20, spaceAfter=10)
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontName="Helvetica-Bold",
        fontSize=13,
        caseChange='upper',     # 🔠 deixa tudo maiúsculo
        textColor=colors.HexColor("#007BFF")  # 🔹 Azul moderno
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName="Helvetica",
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        # alignment=TA_JUSTIFY
    )

    elementos = []
    # Capa
    elementos.append(
        Paragraph(f"Relatório de Notícias - {categoria or 'Todas'}", title_style))
    elementos.append(Paragraph(
        f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))

    # Agrupa notícias por região
    noticias_por_regiao = defaultdict(list)
    for noticia in noticias:
        regiao = noticia.get("regiao", "Mundo")
        noticias_por_regiao[regiao].append(noticia)

    # Ordem fixa de seções
    regioes_ordem = ["Mundo", "Brasil", "Nordeste", "Piauí"]

    for regiao in regioes_ordem:
        if regiao in noticias_por_regiao:
            elementos.append(Paragraph(f"{regiao.upper()}", section_style))
            for i, noticia in enumerate(noticias_por_regiao[regiao], 1):
                elementos.append(
                    Paragraph(f"{i}. <a href='{noticia.get('link')}'>{noticia.get('titulo', 'Sem título')}</a>", header_style))
                if noticia.get("resumo"):
                    elementos.append(
                        Paragraph(f"Resumo: {noticia.get('resumo')}", body_style))
                elementos.append(
                    Paragraph(f"Fonte: {noticia.get('fonte', 'Desconhecida')}", body_style))
                elementos.append(
                    Paragraph(f"Data: {noticia.get('data', '-')}", body_style))
                elementos.append(
                    Paragraph(f"Categoria: {noticia.get('categoria', '-')}", body_style))
                elementos.append(Spacer(1, 12))
            elementos.append(PageBreak())

    doc.build(elementos)
    print(f"✅ PDF gerado: {nome_arquivo}")
