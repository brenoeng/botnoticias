import os
import requests
from dotenv import load_dotenv
# --- Carregar variáveis do .env ---
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

url = "https://newsapi.org/v2/top-headlines/sources"
params = {"apiKey": NEWS_API_KEY, "language": "pt"}
resp = requests.get(url, params=params).json()
for fonte in resp["sources"]:
    print(fonte["id"], "-", fonte["name"])
