import os
from reportlab.lib.units import inch
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.utils import ImageReader  # Importação para a imagem
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY

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


def gerar_pdf(noticias: List[Dict], nome_arquivo: str = "relatorio_setorial.pdf", categoria: Optional[str] = None):
    """
    Gera um PDF agrupando notícias por sua 'fonte' (site oficial).

    Args:
        noticias (List[Dict]): Lista de dicionários de notícias com chaves 'fonte',
                               'titulo', 'link', 'data', 'resumo', 'categoria'.
        nome_arquivo (str): Nome do arquivo PDF a ser gerado.
        categoria (Optional[str]): Categoria geral do relatório (ex: 'Energia').
    """
    # Pasta onde os PDFs serão salvos
    pasta_pdf = "relatorios"
    # 2. Constrói o caminho completo: "relatorios/" + nome_arquivo
    caminho_completo = os.path.join(path, pasta_pdf, nome_arquivo)

    doc = SimpleDocTemplate(caminho_completo, pagesize=A4)
    styles = getSampleStyleSheet()

    # --- Estilos de Parágrafo ---
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Title'], fontName="Helvetica", fontSize=18, spaceAfter=20, alignment=1)
    subtitle_style = ParagraphStyle(
        'SubtitleStyle', parent=styles['Normal'], fontName="Helvetica", fontSize=12, spaceAfter=30, alignment=1)
    # Estilo para o nome do site/fonte
    section_style = ParagraphStyle(
        'SectionStyle', parent=styles['Heading1'], fontName="Helvetica-bold", fontSize=16, spaceBefore=25, spaceAfter=12,
        textColor=colors.HexColor("#0056b3")  # Azul escuro
    )
    # Estilo para o TÍTULO da Notícia (com link)
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontName="Helvetica-bold",
        fontSize=13,
        leftIndent=20,
        caseChange='upper',
        textColor=colors.HexColor("#343a40")  # Cinza escuro
    )
    # Estilo para Resumo e Detalhes
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName="Helvetica",
        leftIndent=20,
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        alignment=TA_JUSTIFY,
        spaceAfter=5
    )
    # --- Fim dos Estilos ---

    elementos = []

    # 1. Capa
    elementos.append(
        Paragraph(f"Informativo - Setor {categoria or 'Energético'}", title_style))
    elementos.append(Paragraph(
        f"MME, ONS, ANEEL, EPE e Petrobras", subtitle_style))
    elementos.append(Paragraph(
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y')}", subtitle_style))
    # elementos.append(PageBreak())

    # 2. Agrupa notícias por Fonte
    noticias_por_fonte = defaultdict(list)
    for noticia in noticias:
        fonte = noticia.get("fonte", "Fonte Desconhecida")
        noticias_por_fonte[fonte].append(noticia)

    # 3. Ordem fixa de fontes para organização lógica
    # Os nomes devem coincidir exatamente com o que é retornado nas suas funções de scraping.
    fontes_ordem = [
        "Ministério de Minas e Energia (MME)",
        "Operador Nacional do Sistema Elétrico (ONS)",
        "Agência Nacional de Energia Elétrica (ANEEL)",
        "Empresa de Pesquisa Energética (EPE)",
        "Agência Petrobras de Notícias",
        "Fonte Desconhecida"  # Para qualquer notícia que não tenha fonte
    ]

    # 4. Construção do corpo do PDF
    total_fontes = len(noticias_por_fonte)
    fontes_processadas = 0

    for fonte in fontes_ordem:
        if fonte in noticias_por_fonte:
            fontes_processadas += 1

            # Título da Seção (Nome do Site)
            elementos.append(Paragraph(f"{fonte}", section_style))
            # elementos.append(Spacer(1, 1))

            for i, noticia in enumerate(noticias_por_fonte[fonte], 1):
                # Título da Notícia (com link)
                # Adiciona o número do item e o link clicável
                elementos.append(
                    Paragraph(f"{i}. <a href='{noticia.get('link')}'>{noticia.get('titulo', 'Sem título')}</a>", header_style))

                # Resumo
                if noticia.get("resumo"):
                    elementos.append(
                        Paragraph(f"{noticia.get('resumo')}", body_style))

                # Data e Categoria
                elementos.append(
                    Paragraph(f"Data: {noticia.get('data', '-')} | Categoria: {noticia.get('categoria', '-')}", body_style))

                elementos.append(Spacer(1, 10))  # Espaço entre notícias

            # Adiciona quebra de página se não for a última seção
            if fontes_processadas < total_fontes and fontes_processadas != len(fontes_ordem):
                # elementos.append(PageBreak())
                continue

                # 5. Geração final do PDF
    # Constrói o documento, passando a função do template para 'onFirstPage' e 'onLaterPages'
    doc.build(
        elementos,
        onFirstPage=header_footer_template,
        onLaterPages=header_footer_template
    )
    print(f"✅ PDF gerado: {caminho_completo}")


# --- Execução de Exemplo ---
# Se você quiser testar esta função, descomente as linhas abaixo
# gerar_pdf(noticias_exemplo,
#           nome_arquivo="relatorio_petrobras_ons_mme.pdf", categoria="Energia")
