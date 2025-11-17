from datetime import datetime
import os
from collections import defaultdict
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader  # Importação para a imagem
from reportlab.lib.units import inch  # Importação para as unidades


# --- Configuração da Imagem do Template ---
# Ajuste o caminho conforme necessário para o seu arquivo de imagem
pasta_images = 'images'
path = os.path.abspath(os.path.dirname(__file__))
img_path = os.path.join(path, pasta_images, 'template.png')


def header_footer_template(canvas, doc):
    """Função que será chamada para desenhar o cabeçalho/rodapé em cada página,
    incluindo a imagem de fundo/cabeçalho.
    """
    canvas.saveState()

    page_width, page_height = A4

    # --- Configurações do Template (Baseado em inseririmagem.py) ---
    margin = 1 * inch

    # 1. Desenhar a Imagem do Cabeçalho/Fundo
    try:
        img = ImageReader(img_path)

        # Posição e dimensões para preencher a página (ajuste conforme o template)
        # Este código do inseririmagem.py parece desenhar a imagem na página inteira
        # ou na largura total (page_width) e altura A4[1] (altura total).
        x_start = 0
        y_start = 0

        canvas.drawImage(
            img,
            x_start,
            y_start,
            width=page_width,
            height=page_height,  # Usando page_height para cobrir toda a altura
            # preserveAspectRatio=True # Descomente se quiser manter proporção
        )

    except Exception as e:
        # Se a imagem não for encontrada, o PDF ainda será gerado.
        print(f"Erro ao carregar imagem no template: {e}")

    # 2. Desenhar um Rodapé: Número da Página
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 11)
    page_num_text = "%s" % doc.page
    # Ajusta a posição para ser legível sobre o fundo/template
    # 50 é um offset, margin/2 é a altura do rodapé
    canvas.drawString(page_width - margin - 10, 10, page_num_text)

    canvas.restoreState()


def gerar_pdf(noticias, nome_arquivo="noticias.pdf", categoria=None):
    # Cria o documento. Adicionamos margens para que o conteúdo não fique sob o template.
    # Ajuste as margens se o seu template for apenas para o cabeçalho.
    margin_top_content = 1.5 * inch  # Mais espaço no topo para o template
    margin_bottom_content = 0.75 * inch  # Espaço para o rodapé
    margin_sides = 0.75 * inch

    # Pasta onde os PDFs serão salvos
    pasta_pdf = "relatorios"
    # 2. Constrói o caminho completo: "relatorios/" + nome_arquivo
    caminho_completo = os.path.join(path, pasta_pdf, nome_arquivo)

    # 3. Cria a pasta 'relatorios' se ela não existir
    if not os.path.exists(pasta_pdf):
        os.makedirs(pasta_pdf)
    # -----------------------------------------------------------

    doc = SimpleDocTemplate(
        caminho_completo,
        pagesize=A4,
        topMargin=margin_top_content,
        bottomMargin=margin_bottom_content,
        leftMargin=margin_sides,
        rightMargin=margin_sides
    )
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
    section_equipe_style = ParagraphStyle(
        'SectionEquipeStyle', parent=styles['Heading1'], fontName="Helvetica-Bold", fontSize=14, spaceBefore=20, spaceAfter=10, alignment=1)
    nome_style = ParagraphStyle(
        'NomeStyle',
        parent=styles['Normal'],
        fontName="Helvetica",
        fontSize=12,
        # textColor=colors.HexColor("#555555"),
        alignment=1,
        spaceAfter=5
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
                # elementos.append(
                # Paragraph(f"Categoria: {noticia.get('categoria', '-')}", body_style))
                elementos.append(Spacer(1, 12))
            elementos.append(PageBreak())

    elementos.append(
        Paragraph("ORGANIZAÇÃO E ELABORAÇÃO – SUMER", section_equipe_style))
    elementos.append(Paragraph(
        "SUPERINTENDÊNCIA DE MINERAÇÃO E ENERGIAS RENOVÁVEIS (SUMER)", section_equipe_style))
    elementos.append(Paragraph(
        "Bruno Casanova Cerullo", nome_style))
    elementos.append(Paragraph(
        "Diretoria de Mineração e Energias Renováveis (DIMER)", section_equipe_style))
    elementos.append(Paragraph(
        "Gabriela Oliveira Rodrigues", nome_style))
    elementos.append(Paragraph(
        "Gerência de Energias Renováveis (GEER)", section_equipe_style))
    elementos.append(Paragraph(
        "Hizadora Silva Lima", nome_style))
    elementos.append(Paragraph(
        "Gerência de Planejamento e Relações Institucionais (GEPL)", section_equipe_style))
    elementos.append(Paragraph(
        "Jéssica Mayara Mendes de Sousa", nome_style))
    elementos.append(Paragraph(
        "Equipe de Elaboração", section_equipe_style))
    elementos.append(Paragraph(
        "Breno Avelar Rodrigues de Andrade", nome_style))
    elementos.append(Paragraph(
        "Hizadora Silva Lima", nome_style))

    # Constrói o documento, passando a função do template para 'onFirstPage' e 'onLaterPages'
    doc.build(
        elementos,
        onFirstPage=header_footer_template,
        onLaterPages=header_footer_template
    )
    print(f"✅ PDF gerado: {caminho_completo}")
