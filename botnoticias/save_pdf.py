from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from datetime import datetime

# Função para cabeçalho e rodapé


def header_footer(canvas, doc, header_img="header.png", footer_img="footer.png"):
    width, height = A4

    # Cabeçalho
    try:
        canvas.drawImage(header_img, 40, height - 60, width=120,
                         height=40, preserveAspectRatio=True, mask='auto')
    except:
        pass  # se a imagem não existir, ignora

    # Rodapé
    try:
        canvas.drawImage(footer_img, 40, 20, width=120,
                         height=40, preserveAspectRatio=True, mask='auto')
    except:
        pass

    # Número da página
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - 40, 30, f"Página {doc.page}")


def save_pdf(news_list, filename="noticias_estilizadas.pdf", header_img="./images/header.png", footer_img="./images/footer.png"):
    # Cria documento
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor("#2E86C1"),
        spaceAfter=15,
        alignment=1  # centralizado
    )
    news_title_style = ParagraphStyle(
        'NewsTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#117A65"),
        spaceAfter=10,
    )
    news_text_style = ParagraphStyle(
        'NewsText',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=12,
    )

    # Capa
    story.append(
        Paragraph("📢 Notícias de Energia e Mineração no Piauí", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(PageBreak())

    # Notícias
    for i, news in enumerate(news_list, start=1):
        title = news.get("title", "Sem título")
        link = news.get("url", "#")

        # Caixa com título da notícia
        story.append(Paragraph(f"📰 {i}. {title}", news_title_style))
        story.append(
            Paragraph(f"<a href='{link}' color='blue'>{link}</a>", styles['Normal']))
        story.append(Spacer(1, 6))
        story.append(
            Paragraph(news.get("summary", "Sem resumo disponível."), news_text_style))

        # Linha divisória
        data = [[" "]]
        table = Table(data, colWidths=[450])
        table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(table)
        story.append(Spacer(1, 15))

    # Gera PDF com cabeçalho/rodapé
    # Gera PDF com cabeçalho/rodapé
    doc.build(story, onFirstPage=lambda c, d: header_footer(c, d, header_img, footer_img),
              onLaterPages=lambda c, d: header_footer(c, d, header_img, footer_img))
