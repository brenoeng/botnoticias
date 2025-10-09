# botnoticias/test_pdf_generator.py

from pdf_generator import gerar_pdf
from datetime import datetime


sample_noticias = [
    {
        "regiao": "Mundo",
        "titulo": "Notícia Mundial",
        "fonte": "Agência Global",
        "data": "2024-06-01",
        "categoria": "Energia",
        "link": "https://example.com/mundo",
        "resumo": "Resumo mundial."
    },
    {
        "regiao": "Brasil",
        "titulo": "Notícia Brasil",
        "fonte": "Agência Brasil",
        "data": "2024-06-02",
        "categoria": "Mineração",
        "link": "https://example.com/brasil",
        "resumo": "Resumo Brasil."
    },
    {
        "regiao": "Piauí",
        "titulo": "Notícia Piauí",
        "fonte": "Jornal Piauí",
        "data": "2024-06-03",
        "categoria": "Energia",
        "link": "https://example.com/piaui",
        "resumo": "Resumo Piauí."
    },
    {
        "regiao": "Nordeste",
        "titulo": "Notícia Nordeste",
        "fonte": "Jornal Nordeste",
        "data": "2024-06-04",
        "categoria": "Mineração",
        "link": "https://example.com/nordeste",
        "resumo": "Resumo Nordeste."
    }
]

gerar_pdf(sample_noticias,
          nome_arquivo=f"testePDFgerar_{datetime.now().strftime('%d-%m-%Y')}.pdf", categoria="Teste")
