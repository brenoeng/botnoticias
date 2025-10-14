import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta  # Importamos as ferramentas de data
from typing import List, Dict
import locale


def get_epe() -> List[Dict]:
    """
    Faz uma requisição para a página de notícias do EPE, extrai título, link e data,
    e filtra apenas as notícias publicadas nos últimos 7 dias.
    """
    url = "https://www.epe.gov.br/pt/imprensa/noticias/area"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    artigos = []

    # 1. Definir o limite de tempo (Hoje - 7 dias)
    # Primeiro, ajustamos a localização para garantir o tratamento correto do mês, se necessário
    # Embora a data seja D/M/A, é uma boa prática em scraping.
    try:
        # Tenta definir para português brasileiro
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except locale.Error:
        # Se não conseguir, tenta um padrão
        try:
            locale.setlocale(locale.LC_TIME, 'portuguese')
        except locale.Error:
            pass  # Continua mesmo sem o locale

    hoje = datetime.now().date()
    data_limite = hoje - timedelta(days=7)  # Calcula a data de 7 dias atrás

    # 2. Iterar e Filtrar
    for item in soup.select("div.item"):
        # Extração do TÍTULO e LINK (sem alterações)
        tag_a = item.find('a')

        if not tag_a:
            continue

        titulo = tag_a.get_text(strip=True)
        link = tag_a.get("href")

        # 3. Extrair e Converter a DATA
        tag_data = item.find('span', class_='date')

        if not tag_data:
            continue

        data_str = tag_data.get_text(strip=True).split()[0]

        # 4. Extrair RESUMO (se disponível)
        tag_resumo = item.find('p', class_='small')
        # print(tag_resumo)
        resumo_com_data = tag_resumo.get_text(strip=True) if tag_resumo else ""
        # O resumo vem com a data no início, então removemos a data do início
        resumo_com_tags = resumo_com_data.split("-", 1)[-1]
        resumo = resumo_com_tags.rsplit(
            ".", 1)[0] + "." if resumo_com_tags else ""

        # extração CATEGORIA (se disponível)
        tag_categoria = item.find_all('a', class_='tag-area')
        # print(tag_categoria)
        categorias = []
        for categoria in tag_categoria:
            categorias.append(categoria.get_text(strip=True))
        categoria = ", ".join(categorias)

        try:
            # Converte a string (ex: "26/09/2025") para um objeto date do Python
            # %d/%m/%Y é o formato para Dia/Mês/Ano
            data_noticia = datetime.strptime(
                data_str, '%d/%m/%Y').date()
        except ValueError as e:
            # Em caso de erro na conversão (formato inesperado), pula esta notícia
            print(f"Erro ao processar a data '{data_str}': {e}")
            continue

        # 4. O FILTRO: Verifica se a data da notícia é maior ou igual à data limite
        if data_noticia >= data_limite:
            # Formatar o link para ser absoluto
            if link and not link.startswith("http"):
                link = "https://www.epe.gov.br" + link

            # Adicionar ao array de artigos
            artigos.append({
                "fonte": "Empresa de Pesquisa Energética (EPE)",
                "titulo": titulo,
                "link": link,
                "data": data_str,  # Mantemos a string original para o output
                "resumo": resumo,  # O EPE não fornece resumo na listagem
                "categoria": categoria if categoria else "Sem categoria"
            })
        else:
            # Opcional: Para otimizar, se a página estiver em ordem cronológica reversa
            # (mais nova primeiro), podemos parar de iterar assim que encontrarmos
            # uma notícia mais antiga que o limite.
            # print(f"Notícia {titulo} é muito antiga ({data_str}). Parando...")
            pass  # Descomente a linha acima se quiser otimizar o loop.

    return artigos


# Exemplo de uso:
noticias = get_epe()
# for noticia in noticias:
#     print(
#         f"Título: {noticia['titulo']} \n Data: {noticia['data']} \n Link: {noticia['link']}")
#     print("-" * 80)
# # print(noticias)
# print(f"  → {len(noticias)} artigos encontrados no EPE.")
