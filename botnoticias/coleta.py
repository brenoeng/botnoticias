from datetime import datetime, timedelta
import requests
import re
from GoogleNews import GoogleNews
from config import NEWS_API_KEY, GNEWS_API_KEY, LANGUAGE, QUERIES, FROM_DATE, TO_DATE

# Funções para NewsAPI e GNews


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
    # print("🔎 Buscando:", params["q"])
    # print("URL gerada:", requests.Request(
    #     "GET", url, params=params).prepare().url)

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

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
    # print("🔎 Buscando:", query)
    # print("URL gerada:", url)
    resp = requests.get(url).json()
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
    """
    Busca notícias usando a biblioteca GoogleNews e retorna uma lista 
    de dicionários no mesmo formato do seu NewsAPI original.

    Args:
        query (str): O termo de busca para as notícias.
    """

    try:
        # Inicializa e configura a busca
        googlenews = GoogleNews(
            lang=LANGUAGE,
            region='BR',
            period='1d'
        )

        # Faz a busca
        googlenews.search(query)

        # Retorna todos os resultados encontrados
        resultados = googlenews.results()

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar Google News: {e}")
        return []
    except Exception as e:
        print(f"Erro inesperado durante a busca: {e}")
        return []

    artigos = []
    for art in resultados:
        # A data da GoogleNews vem em formato mais amigável, mas nem sempre padronizado.
        # Vamos tentar extrair a data e formatá-la (se necessário)

        # O campo 'date' da GoogleNews é geralmente algo como "X horas atrás" ou "dd/mm/yyyy"
        data_publicacao = normalizar_data_google(art.get("date"))
        if data_publicacao == "Data desconhecida":
            continue

        link = art.get("link", "#") or "#"
        # Limpa parâmetros extras (&ved, &usg, etc.)
        if "&" in link:
            link = link.split("&")[0]

        artigos.append({
            "fonte": art.get("media", "Fonte desconhecida"),
            "titulo": art.get("title", "Sem título"),
            "link": link,
            "data": data_publicacao  # Mantemos o formato original da GoogleNews
        })

    print(f"  → {len(artigos)} artigos encontrados em Google News.")

    return artigos

# Função principal para coletar todas as notícias


def coletar_noticias_por_categoria(max_por_query=5, debug=False):
    """
    Coleta notícias de todas as fontes para cada query configurada.
    Limita o total a `max_por_query` notícias mais recentes por query.
    Se debug=True, exibe os títulos das notícias selecionadas.
    """
    results = []
    seen = set()

    for categoria, queries in QUERIES.items():
        print(f"\n📡 Coletando categoria: {categoria}")
        for query in queries:
            print(f"   🔍 Buscando por: {query}")
            noticias_query = []

            # fontes de coleta
            for func in [get_newsapi, get_gnews, get_google_news]:
                try:
                    fontes = func(query)
                    noticias_query.extend(fontes)
                except Exception as e:
                    print(f"   ⚠️ Erro em {func.__name__} ({query}): {e}")

            # 🔹 Remove duplicadas (pelo link)
            noticias_unicas = []
            seen_links = seen  # O conjunto 'seen' rastreia links
            seen_titles_4_words = set()  # Rastreia chaves de título de 4 palavras
            for art in noticias_query:
                art['titulo'] = art.get('titulo', 'Sem título').strip()

                # """Limpa, normaliza e retorna as 4 primeiras palavras do título como uma chave única."""
                # Remove pontuação, acentos e caracteres especiais, converte para minúsculas
                title = re.sub(r'[^\w\s]', '', art['titulo']).lower()
                # Remove espaços múltiplos e divide em palavras
                tokens = re.sub(r'\s+', ' ', title).strip().split()

                # Pega as 4 primeiras palavras e junta-as. Retorna string vazia se for muito curto.
                title_key = " ".join(
                    tokens[:4]) if len(tokens) >= 4 else ""

                # Condição de unicidade: Link não visto E (Chave de título válida E chave não vista)
                # Note que se a chave de título for vazia (título muito curto),
                # ela não impede a inclusão, dependendo apenas do link.
                is_title_key_new = not title_key or (
                    title_key not in seen_titles_4_words)

                if art["link"] and art["link"] not in seen_links and is_title_key_new:
                    seen_links.add(art["link"])
                    if title_key:
                        seen_titles_4_words.add(title_key)
                    noticias_unicas.append(art)

            # 🔹 Ordena por data e limita a 5 mais recentes
            noticias_unicas.sort(key=lambda n: n.get("data", ""), reverse=True)
            noticias_limite = noticias_unicas[:max_por_query]

            print(
                f"   → Mantendo {len(noticias_limite)} notícias da query '{query}'")

            if debug:
                for n in noticias_limite:
                    print(f"      📰 {n.get('titulo', 'Sem título')}")

            # # 🔹 Adiciona categoria e região
            for art in noticias_limite:
                art["categoria"] = categoria
                art["regiao"] = "Mundo"  # Valor inicial
                results.append(art)

    print(
        f"\n✅ Total final de notícias coletadas (todas categorias): {len(results)}")
    return results
