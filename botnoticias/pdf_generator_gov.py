from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional

# --- Simulação de Notícias (Use o resultado de suas funções de scraping reais) ---
# Este bloco é apenas para demonstração.
# noticias_exemplo = [
#     {
#         "fonte": "Ministério de Minas e Energia (MME)",
#         "titulo": "MME lança programa de incentivo à solar",
#         "link": "http://mme.gov.br/noticia1",
#         "data": "10/10/2025",
#         "resumo": "O novo programa visa subsidiar a instalação de painéis solares em regiões isoladas.",
#         "categoria": "Energia",
#     },
#     {
#         "fonte": "Agência Petrobras de Notícias",
#         "titulo": "Petrobras bate recorde de produção no pré-sal",
#         "link": "http://agencia.petrobras.com.br/noticiaA",
#         "data": "12/10/2025",
#         "resumo": "A produção diária de barris superou as expectativas do mercado para o trimestre.",
#         "categoria": "Negócios",
#     },
#     {
#         "fonte": "Operador Nacional do Sistema Elétrico (ONS)",
#         "titulo": "Carga de energia atinge novo pico de demanda",
#         "link": "http://ons.org.br/pico",
#         "data": "09/10/2025",
#         "resumo": "O crescimento econômico impulsiona o consumo, exigindo novas expansões na rede.",
#         "categoria": "Infraestrutura",
#     },
#     {
#         "fonte": "Ministério de Minas e Energia (MME)",
#         "titulo": "Novos leilões de transmissão anunciados",
#         "link": "http://mme.gov.br/leilao",
#         "data": "11/10/2025",
#         "resumo": "O governo espera atrair R$ 5 bilhões em investimentos.",
#         "categoria": "Regulatório",
#     },
#     {
#         "fonte": "Empresa de Pesquisa Energética (EPE)",
#         "titulo": "EPE projeta queda no preço da eólica até 2030",
#         "link": "http://epe.gov.br/eolica",
#         "data": "08/10/2025",
#         "resumo": "A maturidade tecnológica e a escala de produção devem reduzir custos.",
#         "categoria": "Pesquisa",
#     },
#     # Adicione aqui notícias da ANEEL e outras fontes quando tiver os dados reais
# ]
# # --------------------------------------------------------------------------


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
        'TitleStyle', parent=styles['Title'], fontName="Times-Bold", fontSize=22, spaceAfter=20, alignment=1)
    subtitle_style = ParagraphStyle(
        'SubtitleStyle', parent=styles['Normal'], fontName="Times-Bold", fontSize=12, spaceAfter=30, alignment=1)
    # Estilo para o nome do site/fonte
    section_style = ParagraphStyle(
        'SectionStyle', parent=styles['Heading1'], fontName="Times-Bold", fontSize=16, spaceBefore=25, spaceAfter=12,
        textColor=colors.HexColor("#0056b3")  # Azul escuro
    )
    # Estilo para o TÍTULO da Notícia (com link)
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontName="Times-Bold",
        fontSize=13,
        caseChange='upper',
        textColor=colors.HexColor("#343a40")  # Cinza escuro
    )
    # Estilo para Resumo e Detalhes
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName="Times",
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        alignment=TA_JUSTIFY,
        spaceAfter=5
    )
    # --- Fim dos Estilos ---

    elementos = []

    # 1. Capa
    elementos.append(
        Paragraph(f"Relatório de Notícias - Setor {categoria or 'Energético'}", title_style))
    elementos.append(Paragraph(
        f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
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
            elementos.append(Spacer(1, 6))

            for i, noticia in enumerate(noticias_por_fonte[fonte], 1):
                # Título da Notícia (com link)
                # Adiciona o número do item e o link clicável
                elementos.append(
                    Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{i}. <a href='{noticia.get('link')}'>{noticia.get('titulo', 'Sem título')}</a>", header_style))

                # Resumo
                if noticia.get("resumo"):
                    elementos.append(
                        Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;Resumo: {noticia.get('resumo')}", body_style))

                # Data e Categoria
                elementos.append(
                    Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;Data: {noticia.get('data', '-')} | Categoria: {noticia.get('categoria', '-')}", body_style))

                elementos.append(Spacer(1, 10))  # Espaço entre notícias

            # Adiciona quebra de página se não for a última seção
            if fontes_processadas < total_fontes and fontes_processadas != len(fontes_ordem):
                elementos.append(PageBreak())

    # 5. Geração final do PDF
    doc.build(elementos)
    print(f"✅ PDF gerado: {nome_arquivo}")


# --- Execução de Exemplo ---
# Se você quiser testar esta função, descomente as linhas abaixo
# gerar_pdf(noticias_exemplo,
#           nome_arquivo="relatorio_petrobras_ons_mme.pdf", categoria="Energia")
