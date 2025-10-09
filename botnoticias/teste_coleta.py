import requests
from bs4 import BeautifulSoup
from coleta import coletar_noticias_por_categoria, get_newsapi, get_gnews, get_google_news
from datetime import datetime, timedelta
from pdf_generator import gerar_pdf
from ia_filter import filtrar_e_resumir_noticia
# O módulo 're' não é mais necessário, pois estamos lendo o atributo datetime padronizado.


def imprimir_noticias(noticias):
    for noticia in noticias:
        print(f"Título: {noticia['titulo']}")
        print(f"Fonte: {noticia['fonte']}")
        print(f"Link: {noticia['link']}")
        print(f"Data: {noticia['data']}")
        print("-" * 40)


MAX_NOTICIAS_IA = 20

if __name__ == '__main__':
    # Você precisará ter as bibliotecas requests e beautifulsoup4 instaladas
    # pip install requests beautifulsoup4

    resultados = coletar_noticias_por_categoria(debug=True)
    print(f"Total de notícias encontradas: {len(resultados)}")

    print("\n--- Resultados (Máx. 7 Dias) ---")
    imprimir_noticias(resultados[:5])

    # if resultados:
    #     for i, art in enumerate(resultados[:10]):
    #         print(f"[{i+1}] {art['titulo']}")
    #         print(
    #             f"    Fonte: {art['fonte']} | Publicado em: {art['data']}")
    #         print(f"    Link: {art['link']}\n")
    # else:
    #     print("Nenhum artigo encontrado dentro do limite de 7 dias.")
    gerar_pdf(resultados, nome_arquivo="teste_noticias.pdf", categoria="Teste")
    print("PDF de teste gerado: teste_noticias.pdf")

    # a = filtrar_e_resumir_noticia(resultados[1], debug=True)
    # print("Resultado do filtro IA:", a)

    # print("Teste de filtro IA concluído.")
