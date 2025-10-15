import time
import json
from google import genai
from google.genai import errors
from config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

# 🚨 VARIÁVEIS DE CONTROLE DE RATE LIMIT 🚨
# Limite: 10 requisições por minuto (10 RPM)
RPM_LIMIT = 10
# 60 segundos / 10 requisições = 6.0 segundos por requisição
DELAY_SECONDS = 60 / RPM_LIMIT
LAST_REQUEST_TIME = 0.0  # Guarda o timestamp da última requisição
# request_lock = Lock() # Usar se o código for chamado de múltiplos threads


def wait_for_rate_limit():
    """Calcula e espera o tempo necessário para respeitar o limite de 10 RPM."""
    global LAST_REQUEST_TIME

    current_time = time.time()

    # Calcula o tempo que passou desde a última requisição
    elapsed_time = current_time - LAST_REQUEST_TIME

    # Calcula o tempo que precisamos esperar
    wait_time = DELAY_SECONDS - elapsed_time

    if wait_time > 0:
        # Se o tempo de espera for positivo, aguarda
        print(
            f"⏳ Esperando {wait_time:.2f} segundos para respeitar o limite de 10 RPM...")
        time.sleep(wait_time)

    # Atualiza o timestamp da última requisição para o momento em que a nova requisição
    # DEVE começar (após a espera, se houve)
    LAST_REQUEST_TIME = time.time()


def filtrar_e_resumir_noticia(noticia, model_name=None, max_retries=3, debug=False):
    """
    Analisa se a notícia é relevante para o planejamento do Governo do Piauí.
    A saída sempre é JSON com: relevante, resumo, categoria, regiao.
    """

    model = model_name or GEMINI_MODEL or "gemini-2.5-flash"

    # Define o schema esperado
    json_schema = {
        "type": "object",
        "properties": {
            "relevante": {"type": "boolean", "description": "True se a notícia for relevante para o Piauí em energia ou mineração."},
            "resumo": {"type": "string", "description": "Resumo curto em 1 frase."},
            "categoria": {"type": "string", "enum": ["Energia", "Mineração"], "description": "A categoria da notícia."},
            "regiao": {"type": "string", "description": "A região mencionada na notícia. Escolha entre: Piauí, Nordeste, Brasil, ou Mundo."},
        },
        "required": ["relevante", "resumo", "categoria", "regiao"]
    }

    prompt = f"""
    Você é analista do Governo do Piauí.
    Diga se a notícia é RELEVANTE para o planejamento estadual em energia ou mineração.

    Responda SOMENTE em JSON, no formato:
    {{
      "relevante": true/false,
      "resumo": "Resumo curto em 1 frase",
      "categoria": "Energia" ou "Mineração",
      "regiao": "Piauí" ou "Nordeste" ou "Brasil" ou "Mundo"
    }}

    Título: {noticia.get('titulo', '')}
    """
    # Fonte: {noticia.get('fonte', '')}
    # Link: {noticia.get('link', '')}
    # Categoria: {noticia.get('categoria', '-')}
    # Região: {noticia.get('regiao', '-')}

    for attempt in range(max_retries):
        try:

            wait_for_rate_limit()

            # 💡 Use a configuração de resposta para forçar o JSON!
            resp = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": json_schema
                }
            )

            # 💡 Acessando os metadados de uso
            usage = resp.usage_metadata

            if debug:
                print(f"Tokens de entrada: {usage.prompt_token_count}")
                print(f"Tokens de saída: {usage.candidates_token_count}")
                print(f"Total de tokens: {usage.total_token_count}")

            texto = resp.text.strip()

            if debug:
                print("🔎 Debug IA resposta bruta:", texto)

            return json.loads(texto)
        except Exception as e:
            if debug:
                print(f"⚠️ Erro IA (tentativa {attempt+1}): {e}")
            time.sleep(2 ** attempt)

    return {
        "relevante": False,
        "resumo": "",
        "categoria": noticia.get("categoria", ""),
        "regiao": noticia.get("regiao", "")
    }
