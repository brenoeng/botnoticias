# 3️⃣ Filtra com IA
    # energia_relevantes, mineracao_relevantes = [], []

    # for noticia in noticias:
    #     resultado = filtrar_e_resumir_noticia(noticia, debug=True)
    #     noticia.update(resultado)

    #     if resultado.get("relevante"):
    #         if resultado["categoria"].lower() == "energia":
    #             energia_relevantes.append(noticia)
    #         else:
    #             mineracao_relevantes.append(noticia)

    #     print(
    #         f"✔️ {noticia['titulo']} -> {resultado.get('relevante')} ({resultado.get('categoria')})")

    # print(f"⚡ Energia relevantes: {len(energia_relevantes)}")
    # print(f"⛏️ Mineração relevantes: {len(mineracao_relevantes)}")

    # # 4️⃣ PDFs finais
    # if energia_relevantes:
    #     gerar_pdf(energia_relevantes, "energia_relevantes.pdf",
    #               categoria="Energia")
    # if mineracao_relevantes:
    #     gerar_pdf(mineracao_relevantes, "mineracao_relevantes.pdf",
    #               categoria="Mineração")