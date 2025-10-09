# --- Pós-filtragem: manter só notícias que mencionam os temas mais de uma vez ---
    # palavras_chave = ["energia", "renovável", "mineração", "Piauí"]
    # filtradas = []
    # for art in artigos:
    #     texto = f"{art.get('title', '')} {art.get('description', '')} {art.get('content', '')}".lower()
    #     score = sum(texto.count(p.lower()) for p in palavras_chave)
    #     if score >= 2:  # só aceita se tiver pelo menos 2 menções
    #         filtradas.append(art)

    # return filtradas[:5]