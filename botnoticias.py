import os
import requests
from dotenv import load_dotenv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# --- Carregar variáveis do .env ---
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# --- Funções auxiliares ---


def fetch_news():
    """
    Busca notícias relevantes sobre energia e mineração no Piauí
    """
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": '"energia" AND "Piauí"',
        "language": "pt",
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY,
        "pageSize": 10
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    artigos = data.get("articles", [])

    # # --- Pós-filtragem: manter só notícias que mencionam os temas mais de uma vez ---
    # palavras_chave = ["energia", "renovável", "mineração", "Piauí"]
    # filtradas = []
    # for art in artigos:
    #     texto = f"{art.get('title', '')} {art.get('description', '')} {art.get('content', '')}".lower()
    #     score = sum(texto.count(p.lower()) for p in palavras_chave)
    #     if score >= 2:  # só aceita se tiver pelo menos 2 menções
    #         filtradas.append(art)

    # return filtradas[:5]


def gerar_pdf(noticias, nome_arquivo="noticias_piaui.pdf"):
    """
    Gera um PDF com as notícias (sem resumo por IA)
    """
    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(
        Paragraph("📄 Notícias - Energia e Mineração no Piauí", styles['Title']))
    elementos.append(Spacer(1, 20))

    for i, noticia in enumerate(noticias, 1):
        titulo = noticia.get("title", "Sem título")
        url = noticia.get("url", "")
        descricao = noticia.get("description", "Sem descrição disponível.")

        elementos.append(Paragraph(f"{i}. {titulo}", styles['Heading2']))
        elementos.append(Paragraph(descricao, styles['Normal']))
        if url:
            elementos.append(
                Paragraph(f"<a href='{url}'>Leia mais</a>", styles['Normal']))
        elementos.append(Spacer(1, 15))

    doc.build(elementos)
    print(f"✅ PDF gerado: {nome_arquivo}")


def main():
    artigos = fetch_news()
    if not artigos:
        print("Nenhuma notícia encontrada.")
        return

    gerar_pdf(artigos)


if __name__ == "__main__":
    main()
