from datetime import datetime
import os
from coleta import coletar_noticias_por_categoria
# Importa a nova função de lote
from ia_filter import filtrar_todas_noticias
from pdf_generator import gerar_pdf

if __name__ == "__main__":
    # Pasta onde os PDFs serão salvos
    pasta_pdf = "relatorios"
    if not os.path.exists(pasta_pdf):
        os.makedirs(pasta_pdf)

    # 1️⃣ Coleta
    # Aumentei o max_por_query pois agora a IA aguenta processar mais rápido
    noticias = coletar_noticias_por_categoria(max_por_query=7, debug=True)
    print(f"📥 Coletadas {len(noticias)} notícias")

    # 2️⃣ PDF bruto
    arquivo_bruto = f"noticias_brutas_{datetime.now().strftime('%d%m%Y')}.pdf"
    gerar_pdf(noticias, arquivo_bruto, categoria="Todas")  # Opcional

    # 3️⃣ Filtra com IA (EM LOTE - Muito mais rápido)
    # Passamos a lista inteira. O batch_size define quantos itens vão por request.
    # Com batch_size=15, 60 notícias levam 4 requisições (~24 segundos totais de wait)
    filtrar_todas_noticias(noticias, batch_size=50, debug=True)

    # Separação das listas baseada no resultado da IA
    energia_relevantes = [n for n in noticias if n.get(
        'relevante') and n.get('categoria') == 'Energia']
    mineracao_relevantes = [n for n in noticias if n.get(
        'relevante') and n.get('categoria') == 'Mineração']

    print(f"⚡ Energia relevantes: {len(energia_relevantes)}")
    print(f"⛏️ Mineração relevantes: {len(mineracao_relevantes)}")

    # 4️⃣ PDFs finais
    data_str = datetime.now().strftime('%d-%m-%Y')

    if energia_relevantes:
        nome_pdf = f"Notícias_Energia_relevantes_{data_str}.pdf"
        gerar_pdf(energia_relevantes, nome_pdf, categoria="Energia")

    if mineracao_relevantes:
        nome_pdf = f"Notícias_Mineracao_relevantes_{data_str}.pdf"
        gerar_pdf(mineracao_relevantes, nome_pdf, categoria="Mineração")

    print("✅ Concluído.")
