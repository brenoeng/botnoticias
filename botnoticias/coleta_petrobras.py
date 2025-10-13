from datetime import datetime, timedelta
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


def get_agencia_petrobras() -> List[Dict]:
    """
    Busca notícias na Agência Petrobras de Notícias usando a estrutura 'text-container'
    e filtra os resultados publicados nos últimos 7 dias.
    """
    url = "https://agencia.petrobras.com.br/mais-recentes"
    artigos = []

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    # 1. Definir o limite de tempo
    # A data de hoje é Monday, October 13, 2025
    hoje = datetime.now().date()
    data_limite = hoje - timedelta(days=7)

    # 2. Localizar os blocos de notícia
    # Baseado na estrutura: o bloco de notícia geralmente contém a div 'text-container'
    # Vamos procurar por todas as 'div.text-container'
    blocos_noticias = soup.select('div.text-container')
    # print(blocos_noticias)

    if not blocos_noticias:
        print("Aviso: Não foram encontrados blocos de notícias com o seletor 'div.text-container'. A estrutura do site pode ter mudado.")
        return []

    for item in blocos_noticias:
        # 3. Extrair Título e Link
        tag_a = item.find('a', class_='editorial-news-card-link')
        # print(f'{tag_a} \n')
        if not tag_a:
            continue

        titulo = tag_a.get_text(strip=True)
        # print(titulo)
        link_relativo = tag_a.get("href")
        # print(link_relativo)
        # print("-" * 80)

        # 5. Extrair Data
        # A tag da data (div class="date") é uma irmã do text-container
        tag_data = item.find('div', class_='date')
        if not tag_data:
            continue

        # A data está dentro do div.date (geralmente em um <span> ou <time>)
        # Buscamos o primeiro texto limpo dentro do div.date
        data_str = tag_data.get_text(strip=True).split()[-1]
        # print(data_str.split()[-1])

        # O resumo não está explícito na imagem, mas vamos tentar extrair o que vier após a data (se houver)
        resumo = item.find_next_sibling('p')
        resumo = resumo.get_text(
            strip=True) if resumo else "Resumo não encontrado"

        # 6. Converter a DATA
        try:
            # A data na Agência Petrobras é geralmente DD/MM/AAAA.
            data_noticia = datetime.strptime(data_str, '%d/%m/%Y').date()

        except ValueError:
            # Tentativa alternativa: se a data vier como 'há X dias' ou 'Mês DD, AAAA'
            # Se a data falhar na conversão padrão, ignoramos (para manter o código simples e focado no filtro)
            continue

        # 7. O FILTRO: Verifica se a data da notícia é maior ou igual à data limite
        if data_noticia >= data_limite:

            # 8. Formatar o link
            if link_relativo and link_relativo.startswith("/w/"):
                link = f"https://agencia.petrobras.com.br{link_relativo}"
            else:
                # Se for link completo ou outro formato inesperado
                link = link_relativo

            # Opcional: Extrair Categoria
            categoria_tag = item.find('p', class_='editoria')
            categoria = categoria_tag.get_text(
                strip=True) if categoria_tag else "Sem categoria"

            # Adicionar ao array de artigos
            artigos.append({
                "fonte": "Agência Petrobras de Notícias",
                "titulo": titulo,
                "link": link,
                "data": data_str,
                "resumo": resumo,
                "categoria": categoria
            })

    print(f"Filtro concluído. Encontrados {len(artigos)} artigos recentes.")
    return artigos


# Exemplo de uso:
# noticias_petro_agencia = get_agencia_petrobras()
# for noticia in noticias_petro_agencia:
#     print(
#         f"Título: {noticia['titulo']} \n Data: {noticia['data']} \n Link: {noticia['link']}")
#     print("-" * 80)
# # print(noticias)
# print(f"  → {len(noticias_petro_agencia)} artigos encontrados na Petrobras.")
