from coleta import coletar_noticias_por_categoria
from ia_filter import filtrar_e_resumir_noticia
from pdf_generator import gerar_pdf
from datetime import datetime

if __name__ == "__main__":
    # 1️⃣ Coleta
    noticias = coletar_noticias_por_categoria(max_por_query=5, debug=True)
    print(f"📥 Coletadas {len(noticias)} notícias")

    # 2️⃣ PDF bruto
    gerar_pdf(noticias, "noticias_brutas.pdf", categoria="Todas")

    # 3️⃣ Filtra com IA
    energia_relevantes, mineracao_relevantes = [], []

    for noticia in noticias:
        resultado = filtrar_e_resumir_noticia(noticia, debug=True)
        noticia.update(resultado)

        if resultado.get("relevante"):
            if resultado["categoria"].lower() == "energia":
                energia_relevantes.append(noticia)
            else:
                mineracao_relevantes.append(noticia)

        print(
            f"✔️ {noticia['titulo']} -> {resultado.get('relevante')} ({resultado.get('categoria')})")

    print(f"⚡ Energia relevantes: {len(energia_relevantes)}")
    print(f"⛏️ Mineração relevantes: {len(mineracao_relevantes)}")

    # 4️⃣ PDFs finais
    if energia_relevantes:
        gerar_pdf(energia_relevantes, f"Energia_relevantes_{datetime.now().strftime('%d-%m-%Y')}.pdf",
                  categoria="Energia")
    if mineracao_relevantes:
        gerar_pdf(mineracao_relevantes, f"Mineracao_relevantes_{datetime.now().strftime('%d-%m-%Y')}.pdf",
                  categoria="Mineração")

    print("✅ Concluído.")
