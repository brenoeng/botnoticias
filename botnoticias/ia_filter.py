import time
import json
from google import genai
from google.genai import errors
from config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

# 🚨 VARIÁVEIS DE CONTROLE DE RATE LIMIT 🚨
RPM_LIMIT = 10
DELAY_SECONDS = 60 / RPM_LIMIT
LAST_REQUEST_TIME = 0.0


def wait_for_rate_limit():
    """Calcula e espera o tempo necessário para respeitar o limite de 10 RPM."""
    global LAST_REQUEST_TIME
    current_time = time.time()
    elapsed_time = current_time - LAST_REQUEST_TIME
    wait_time = DELAY_SECONDS - elapsed_time

    if wait_time > 0:
        print(f"⏳ Esperando {wait_time:.2f}s (Rate Limit)...")
        time.sleep(wait_time)

    LAST_REQUEST_TIME = time.time()


def processar_lote_noticias(lote_noticias, model_name=None, max_retries=3, debug=False):
    """
    Envia um lote de notícias para o Gemini e retorna uma lista de análises.
    """
    model = model_name or GEMINI_MODEL or "gemini-2.5-flash"

    # Define o schema como um ARRAY de objetos
    json_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id_original": {"type": "integer", "description": "O índice numérico fornecido na entrada para identificar a notícia."},
                "relevante": {"type": "boolean", "description": "True se for relevante para o Piauí em energia/mineração."},
                "resumo": {"type": "string", "description": "Resumo curto em 1 frase."},
                "categoria": {"type": "string", "enum": ["Energia", "Mineração"], "description": "Categoria da notícia."},
                "regiao": {"type": "string", "enum": ["Piauí", "Nordeste", "Brasil", "Mundo"], "description": "Região principal."}
            },
            "required": ["id_original", "relevante", "resumo", "categoria", "regiao"]
        }
    }

    # Monta o prompt com todas as notícias do lote
    texto_noticias = ""
    for i, n in enumerate(lote_noticias):
        # Usamos um índice (id_original) para garantir que a IA não perca a ordem
        texto_noticias += f"ID {i}: Título: {n.get('titulo', '')} | Fonte: {n.get('fonte', '')}\n"

    prompt = f"""
    Você é analista do Governo do Piauí. Analise a lista de notícias abaixo.
    Para CADA notícia, determine se é RELEVANTE para o planejamento estadual em energia ou mineração.
    
    Retorne um JSON Array contendo a análise de cada item, mantendo o 'id_original'.

    Notícias:
    {texto_noticias}
    """

    for attempt in range(max_retries):
        try:
            wait_for_rate_limit()

            resp = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": json_schema
                }
            )

            usage = resp.usage_metadata
            if debug:
                print(
                    f"   Tokens In: {usage.prompt_token_count} | Out: {usage.candidates_token_count} | Total: {usage.total_token_count}")

            lista_resultados = json.loads(resp.text)

            # Garante que retornamos uma lista, mesmo que a IA falhe em algo estrutural
            if isinstance(lista_resultados, list):
                return lista_resultados
            else:
                if debug:
                    print("⚠️ IA não retornou uma lista. Tentando novamente.")

        except Exception as e:
            if debug:
                print(f"⚠️ Erro IA Lote (tentativa {attempt+1}): {e}")
            time.sleep(2 ** attempt)

    # Retorno de fallback (lista de erros vazios) caso falhe todas tentativas
    return [{"relevante": False, "resumo": "Erro na análise", "categoria": "-", "regiao": "-", "id_original": i} for i in range(len(lote_noticias))]


def filtrar_todas_noticias(noticias, batch_size=15, debug=True):
    """
    Função principal que orquestra a divisão em lotes e atualização das notícias.
    """
    print(
        f"🤖 Iniciando filtro IA em lotes. Total: {len(noticias)} | Tamanho do lote: {batch_size}")

    count_relevante = 0

    # Processa em chunks (fatias) de tamanho batch_size
    for i in range(0, len(noticias), batch_size):
        lote = noticias[i: i + batch_size]
        if debug:
            print(f"   Processando lote {i} a {i+len(lote)}...")

        resultados_lote = processar_lote_noticias(lote, debug=debug)

        # Mapeia os resultados de volta para as notícias originais
        # Cria um dicionário temporário para acesso rápido por ID
        mapa_resultados = {res.get('id_original')                           : res for res in resultados_lote}

        for idx_local, noticia in enumerate(lote):
            dados_ia = mapa_resultados.get(idx_local)

            if dados_ia:
                noticia['relevante'] = dados_ia.get('relevante', False)
                noticia['resumo'] = dados_ia.get('resumo', '')
                noticia['categoria'] = dados_ia.get(
                    'categoria', noticia.get('categoria'))
                noticia['regiao'] = dados_ia.get('regiao', 'Mundo')
            else:
                # Caso raro onde a IA pula um ID
                noticia['relevante'] = False

            if noticia['relevante']:
                count_relevante += 1
                if debug:
                    print(
                        f"     ✔️ {noticia['titulo'][:30]}... ({noticia['regiao']})")

    print(
        f"✅ Análise concluída. {count_relevante} notícias relevantes identificadas.")
    return noticias
