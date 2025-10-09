import requests
from bs4 import BeautifulSoup
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from datetime import datetime

# ========== CONFIG ==========
NEWS_API_KEY = "SUA_CHAVE_NEWSAPI"
GNEWS_API_KEY = "SUA_CHAVE_GNEWS"
query = "energia mineração Piauí"
language = "pt"

# ================= NEWSAPI =================


def get_newsapi(query):
    url = f"https://newsapi.org/v2/everything?q={query}&language={language}&apiKey={NEWS_API_KEY}"
    resp = requests.get(url).json()
    artigos = []
    for art in resp.get("articles", []):
        artigos.append({
            "fonte": art["source"]["name"],
            "titulo": art["title"],
            "link": art["url"]
        })
    return artigos

# ================= GNEWS =================


def get_gnews(query):
    url = f"https://gnews.io/api/v4/search?q={query}&lang={language}&token={GNEWS_API_KEY}"
    resp = requests.get(url).json()
    artigos = []
    for art in resp.get("articles", []):
        artigos.append({
            "fonte": art["source"]["name"],
            "titulo": art["title"],
            "link": art["url"]
        })
    return artigos

# ================= SCRAPING JORNAIS LOCAIS =================


def get_meio_norte(query):
    url = f"https://www.meionorte.com/busca?q={query.replace(' ', '+')}"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    artigos = []
    for item in soup.select(".busca-resultados a"):
        titulo = item.get_text(strip=True)
        link = item.get("href")
        if titulo and link:
            if not link.startswith("http"):
                link = "https://www.meionorte.com" + link
            artigos.append(
                {"fonte": "Meio Norte", "titulo": titulo, "link": link})
    return artigos


def get_cidade_verde(query):
    url = f"https://cidadeverde.com/busca?q={query.replace(' ', '+')}"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    artigos = []
    for item in soup.select(".title a"):
        titulo = item.get_text(strip=True)
        link = item.get("href")
        if titulo and link:
            if not link.startswith("http"):
                link = "https://cidadeverde.com" + link
            artigos.append(
                {"fonte": "Cidade Verde", "titulo": titulo, "link": link})
    return artigos


def get_o_dia_piaui(query):
    url = f"https://odia.com.br/busca?q={query.replace(' ', '+')}"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    artigos = []
    for item in soup.select(".search-result a"):
        titulo = item.get_text(strip=True)
        link = item.get("href")
        if titulo and link:
            if not link.startswith("http"):
                link = "https://odia.com.br" + link
            artigos.append(
                {"fonte": "O Dia PI", "titulo": titulo, "link": link})
    return artigos

# ================= COLETAR NOTÍCIAS =================


def coletar_noticias(query):
    results = []
    seen = set()
    for func in [get_newsapi, get_gnews, get_meio_norte, get_cidade_verde, get_o_dia_piaui]:
        try:
            for art in func(query):
                if art["link"] not in seen:
                    results.append(art)
                    seen.add(art["link"])
        except Exception as e:
            print(f"Erro em {func.__name__}: {e}")
    return results

# ================= GERAR PDF =================


def gerar_pdf(noticias, nome_arquivo="noticias_piaui.pdf"):
    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
    styles = getSampleStyleSheet()

    # --- Custom Styles ---
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=20,
        alignment=1  # center
    )

    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=30,
        alignment=1
    )

    header_style = styles['Heading2']
    body_style = styles['Normal']

    elementos = []

    # --- Capa ---
    elementos.append(
        Paragraph("📄 Notícias - Energia e Mineração no Piauí", title_style))
    elementos.append(Paragraph(
        f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    elementos.append(PageBreak())

    # --- Notícias ---
    for i, noticia in enumerate(noticias, 1):
        titulo = noticia.get("titulo", "Sem título")
        fonte = noticia.get("fonte", "Fonte desconhecida")
        link = noticia.get("link", "")

        elementos.append(Paragraph(f"{i}. {titulo}", header_style))
        elementos.append(Paragraph(f"Fonte: {fonte}", body_style))
        if link:
            elementos.append(
                Paragraph(f"<a href='{link}'>Leia mais</a>", body_style))
        elementos.append(Spacer(1, 15))

    doc.build(elementos)
    print(f"✅ PDF gerado: {nome_arquivo}")


# ================= EXECUÇÃO =================
if __name__ == "__main__":
    noticias = coletar_noticias(query)
    print(f"Encontradas {len(noticias)} notícias.")
    gerar_pdf(noticias)
