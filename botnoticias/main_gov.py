from datetime import datetime
from coleta_aneel import get_aneel
from coleta_epe import get_epe
from coleta_mme import get_mme
from coleta_ons import get_ons
from coleta_petrobras import get_agencia_petrobras
from pdf_generator_gov import gerar_pdf


def gerar_relatorio():
    """
    Função principal que executa todos os scrapers, combina os resultados
    e gera o relatório PDF.
    """
    todas_noticias = []

    # 1. Coletar dados de todas as fontes
    print("=========================================")
    print("Iniciando coleta de dados de fontes oficiais...")

    # Chame as funções de scraping e combine os resultados
    todas_noticias.extend(get_mme())
    todas_noticias.extend(get_ons())
    todas_noticias.extend(get_aneel())
    todas_noticias.extend(get_epe())
    todas_noticias.extend(get_agencia_petrobras())

    print("=========================================")
    print(
        f"Coleta concluída. Total de {len(todas_noticias)} notícias encontradas.")

    # 2. Gerar PDF
    nome_arquivo = f"Relatorio_Setorial_Completo_{datetime.now().strftime('%d%m%Y')}.pdf"
    gerar_pdf(todas_noticias, nome_arquivo=nome_arquivo,
              categoria="Setor de Energia e Petróleo")

    print(f"Processo finalizado. PDF salvo como: {nome_arquivo}")


# Executa a função principal quando o script é chamado
gerar_relatorio()
