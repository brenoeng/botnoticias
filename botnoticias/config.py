from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

# APIs
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Linguagem
LANGUAGE = "pt"

# ---------------------------------------------
# 🔍 Consultas por categoria
# ---------------------------------------------
QUERIES = {
    "Energia": [
        # Renováveis
        "energia renovável",
        "energia elétrica",
        "energia solar",
        "energia eólica",
        "hidrelétrica",
        "biomassa",
        "biogás",
        "biodiesel",
        # Não renováveis
        "petróleo",
        "gás natural",
        "óleo diesel",
        "carvão mineral",
        "usina termelétrica",
        "combustível fóssil",
        "combustíveis fósseis",
    ],
    "Mineração": [
        "mineração",
        "mineradora",
        "extração mineral",
        "lavra",
        "jazida",
        "garimpo",
        "minério de ferro",
        "ouro mineração",
        "cobre mineração",
        "níquel mineração",
        "lítio mineração",
        "bauxita mineração",
        "fosfato",
        "nióbio",
        "urânio"
    ]
}

# Palavras-chave para filtrar notícias antes da IA
ENERGIA_KEYWORDS = [
    "energia elétrica", "solar", "eólica", "hidrelétrica",
    "petróleo", "gás natural", "biomassa", "biogás", "combustível",
    "renovável", "transmissão", "distribuição", "usina", "óleo diesel"
]

MINERACAO_KEYWORDS = [
    "mineração", "mineradora", "minério", "lavra", "jazida",
    "ferro", "cobre", "níquel", "lítio", "ouro", "extração", "garimpo"
]

# Palavras que indicam falso positivo (quando aparecem sozinhas)
STOPWORDS_FALSOS_POSITIVOS = [
    "corrida", "jogo", "campeonato", "time", "futebol",
    "ouro olímpico", "medalha", "gastronomia", "restaurante"
]


# ---------------------------------------------
# 📅 Intervalo de datas (ontem até antes de ontem)
# ---------------------------------------------
HOJE = datetime.now().date()
FROM_DATE = (HOJE - timedelta(days=2)).strftime("%Y-%m-%d")  # antes de ontem
TO_DATE = (HOJE - timedelta(days=1)).strftime("%Y-%m-%d")    # ontem
