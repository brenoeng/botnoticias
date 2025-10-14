from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY


def gerar_pdf(noticias: List[Dict], nome_arquivo: str = "relatorio_setorial.pdf", categoria: Optional[str] = None):
    """
    Gera um PDF agrupando notícias por sua 'fonte' (site oficial).

    Args:
        noticias (List[Dict]): Lista de dicionários de notícias com chaves 'fonte',
                               'titulo', 'link', 'data', 'resumo', 'categoria'.
        nome_arquivo (str): Nome do arquivo PDF a ser gerado.
        categoria (Optional[str]): Categoria geral do relatório (ex: 'Energia').
    """
    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
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
    doc.build(elementos)
    print(f"✅ PDF gerado: {nome_arquivo}")


# --- Execução de Exemplo ---
# Se você quiser testar esta função, descomente as linhas abaixo
# gerar_pdf(noticias_exemplo,
#           nome_arquivo="relatorio_petrobras_ons_mme.pdf", categoria="Energia")
