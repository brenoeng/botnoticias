from datetime import datetime, timedelta
import requests
import re
from difflib import SequenceMatcher  # Importação para comparar similaridade
from GoogleNews import GoogleNews
from config import NEWS_API_KEY, GNEWS_API_KEY, LANGUAGE, QUERIES, FROM_DATE, TO_DATE

# --- Funções Auxiliares ---


def verificar_similaridade(novo_titulo, lista_titulos, limite=0.85):
    """
    Verifica se o 'novo_titulo' é semelhante a algum item da 'lista_titulos'.
    Retorna True se encontrar similaridade acima do limite.
    """
    # Normaliza para minúsculas para melhorar a comparação
    novo_low = novo_titulo.lower()

    for titulo_existente in lista_titulos:
        ratio = SequenceMatcher(
            None, novo_low, titulo_existente.lower()).ratio()
        if ratio >= limite:
            return True  # É similar (duplicado)
    return False


def get_newsapi(query):
    # Coloca a query entre aspas para busca exata
    query_encoded = f'"{query}"'

    params = {
        "q": query_encoded,
        "language": LANGUAGE,
        "from": FROM_DATE,
        "to": TO_DATE,
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY
    }

    url = "https://newsapi.org/v2/everything"

    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"   ⚠️ Erro na API NewsAPI: {e}")
        return []

    artigos = []
    for art in data.get("articles", []):
        artigos.append({
            "fonte": art["source"]["name"],
            "titulo": art.get("title") or "Sem título",
            "descricao": art.get("description") or "",
            "link": art["url"],
            "data": art.get("publishedAt", "")[:10]  # YYYY-MM-DD
        })
    print(f"  → {len(artigos)} artigos encontrados em Newsapi.")
    return artigos


def get_gnews(query):
    url = (
        f"https://gnews.io/api/v4/search?"
        f"q={query}&lang={LANGUAGE}&from={FROM_DATE}&to={TO_DATE}"
        f"&sortby=publishedAt&max=10&token={GNEWS_API_KEY}"
    )
    try:
        resp = requests.get(url).json()
    except Exception as e:
        print(f"   ⚠️ Erro na API GNews: {e}")
        return []

    artigos = []
    for art in resp.get("articles", []):
        artigos.append({
            "fonte": art["source"]["name"],
            "titulo": art["title"],
            "link": art["url"],
            "data": art.get("publishedAt", "")[:10]
        })
    print(f"  → {len(artigos)} artigos encontrados em Gnews.")
    return artigos


def normalizar_data_google(date_str):
    hoje = datetime.now().date()

    if not date_str:
        return "Data desconhecida"

    date_str = date_str.lower().strip()

    try:
        if "hora" in date_str or "minuto" in date_str:
            return hoje.strftime("%Y-%m-%d")
        elif "ontem" in date_str:
            return (hoje - timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            try:
                return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                return "Data desconhecida"
    except Exception:
        return "Data desconhecida"


def get_google_news(query):
    try:
        googlenews = GoogleNews(
            lang=LANGUAGE,
            region='BR',
            period='1d'
        )
        googlenews.search(query)
        resultados = googlenews.results()

    except Exception as e:
        print(f"Erro ao acessar Google News: {e}")
        return []

    artigos = []
    for art in resultados:
        data_publicacao = normalizar_data_google(art.get("date"))
        if data_publicacao == "Data desconhecida":
            continue

        link = art.get("link", "#") or "#"
        if "&" in link:
            link = link.split("&")[0]

        artigos.append({
            "fonte": art.get("media", "Fonte desconhecida"),
            "titulo": art.get("title", "Sem título"),
            "link": link,
            "data": data_publicacao
        })

    print(f"  → {len(artigos)} artigos encontrados em Google News.")
    return artigos


# --- Função Principal ---

def coletar_noticias_por_categoria(max_por_query=5, debug=False):
    """
    Coleta notícias de todas as fontes, removendo duplicatas por link 
    E por similaridade de título.
    """
    results = []
    seen_links = set()       # Conjunto para links já vistos
    # Lista para títulos já vistos (para fuzzy matching)
    titulos_vistos = []

    for categoria, queries in QUERIES.items():
        print(f"\n📡 Coletando categoria: {categoria}")
        for query in queries:
            print(f"   🔍 Buscando por: {query}")
            noticias_query = []

            # Coleta das fontes
            for func in [get_newsapi, get_gnews, get_google_news]:
                try:
                    fontes = func(query)
                    noticias_query.extend(fontes)
                except Exception as e:
                    print(f"   ⚠️ Erro em {func.__name__} ({query}): {e}")

            # 🔹 Remove duplicadas (Link exato + Título similar)
            noticias_unicas = []

            for art in noticias_query:
                titulo_limpo = art.get('titulo', 'Sem título').strip()
                link = art.get("link")

                # 1. Verifica Link Exato
                if not link or link in seen_links:
                    continue

                # 2. Verifica Similaridade de Título (evita repetição de mesmo assunto de sites diferentes)
                # Se for mais de 85% similar a qualquer título já coletado (mesmo em outras queries), descarta.
                if verificar_similaridade(titulo_limpo, titulos_vistos, limite=0.85):
                    if debug:
                        print(
                            f"      ↳ Duplicata ignorada por similaridade: {titulo_limpo}")
                    continue

                # Se passou nos filtros, adiciona
                seen_links.add(link)
                titulos_vistos.append(titulo_limpo)
                noticias_unicas.append(art)

            # 🔹 Ordena por data e limita a quantidade por query
            noticias_unicas.sort(key=lambda n: n.get("data", ""), reverse=True)
            noticias_limite = noticias_unicas[:max_por_query]

            print(
                f"   → Mantendo {len(noticias_limite)} notícias únicas da query '{query}'")

            if debug:
                for n in noticias_limite:
                    print(f"      📰 {n.get('titulo', 'Sem título')}")

            # Adiciona categoria e metadados finais
            for art in noticias_limite:
                art["categoria"] = categoria
                art["regiao"] = "Mundo"  # Valor inicial
                results.append(art)

    print(
        f"\n✅ Total final de notícias coletadas (todas categorias): {len(results)}")
    return results
