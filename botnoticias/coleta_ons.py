from datetime import datetime, timedelta
import locale
from typing import List, Dict
from bs4 import BeautifulSoup

# --- FERRAMENTAS DO SELENIUM ---
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_ons() -> List[Dict]:
    """
    Busca notícias no site do ONS usando Selenium para renderizar o JavaScript
    e filtra os resultados dos últimos 7 dias.
    """
    url = "https://www.ons.org.br/paginas/imprensa/noticias"  # URL do ONS
    artigos = []

    # 1. Configurar e Iniciar o Selenium (Modo Headless)
    print("Iniciando Selenium para renderizar o conteúdo...")
    options = Options()
    # Roda em segundo plano, sem abrir a janela do navegador
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0...")  # Boa prática

    # Gerencia e instala o driver do Chrome automaticamente
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)

        # Esperar até que a primeira div de notícia real apareça
        # (O "By.CLASS_NAME" deve ser o seletor mais externo que você está usando)
        # Ajuste o tempo se a página demorar muito.
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "noticia")))

        # 2. Obter o HTML Renderizado
        html_renderizado = driver.page_source

    except Exception as e:
        print(f"Erro ao carregar a página com Selenium: {e}")
        driver.quit()
        return []
    finally:
        # 3. Fechar o navegador (MUITO IMPORTANTE)
        driver.quit()

    print("Conteúdo renderizado obtido. Iniciando Beautiful Soup...")

    # 4. Processar o HTML com BeautifulSoup
    soup = BeautifulSoup(html_renderizado, "html.parser")

    # 5. Definir o limite de tempo (igual ao código anterior)
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        pass

    hoje = datetime.now().date()
    data_limite = hoje - timedelta(days=7)

    # 6. Iterar e Filtrar (Ajustado para a nova estrutura do ONS)
    for item in soup.select("div.noticia"):

        # 6.1. Extrair Data
        try:
            dia_str = item.find('div', class_='data').find(
                'p').get_text(strip=True)
            mes_str = item.find('div', class_='data').find(
                'span').get_text(strip=True)
        except AttributeError:
            # Pula se a estrutura estiver incompleta (pode ser o template remanescente)
            continue

        # O ONS geralmente usa o nome do mês (ex: "SET")
        # Precisamos de um dicionário para converter
        mes_map = {
            'JAN': 1, 'FEV': 2, 'MAR': 3, 'ABR': 4, 'MAI': 5, 'JUN': 6,
            'JUL': 7, 'AGO': 8, 'SET': 9, 'OUT': 10, 'NOV': 11, 'DEZ': 12
        }

        # Tenta a conversão da data
        try:
            mes_num = mes_map[mes_str.upper()]
            # Assumimos o ano atual
            ano_atual = hoje.year

            # Cria a string de data no formato D/M/A
            data_completa_str = f"{dia_str}/{mes_num}/{ano_atual}"

            # Converte para objeto datetime
            data_noticia = datetime.strptime(
                data_completa_str, '%d/%m/%Y').date()

            # Filtro de ano: Se o mês for maior que o atual, assume que é do ano passado
            # (Ex: Estamos em Jan/2026, a notícia é de Dez/2025)
            # Obs: Isso é um refinamento, pode ser complexo. Por simplicidade,
            # vamos apenas usar o filtro de 7 dias.

        except (KeyError, ValueError, IndexError):
            # Se a conversão falhar (dados sujos ou template não processado)
            continue

        # 6.2. O FILTRO: Verifica se a data da notícia é maior ou igual à data limite
        if data_noticia >= data_limite:

            # 6.3. Extrair Título, Link e Resumo
            tag_info = item.find('div', class_='info')
            tag_a = tag_info.find('a')

            titulo = tag_a.get_text(strip=True)
            link_relativo = tag_a.get("href")
            resumo = tag_info.find('p').get_text(strip=True)

            # Formata o link
            link = f"{link_relativo}"

            # Adicionar ao array de artigos
            artigos.append({
                "fonte": "Operador Nacional do Sistema Elétrico (ONS)",
                "titulo": titulo,
                "link": link,
                # Data formatada para output
                "data": f"{dia_str}/{mes_str}/{ano_atual}",
                "resumo": resumo
            })

    print(f"Filtro concluído. Encontrados {len(artigos)} artigos recentes.")
    return artigos


# Exemplo de uso:
# noticias_ons = get_ons()
# for noticia in noticias_ons:
#     print(
#         f"Título: {noticia['titulo']} \n Data: {noticia['data']} \n Link: {noticia['link']}")
#     print("-" * 80)
# # print(noticias_ons)
# print(f"  → {len(noticias_ons)} artigos encontrados no MME.")
