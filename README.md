# BotNotícias

Automação em Python para coleta e geração de relatórios de notícias de eletricidade, energética e governo.

## Visão Geral

Este projeto foi criado para facilitar a **extração, filtragem e geração de PDFs** de notícias relevantes sobre energia elétrica, mercados, órgãos reguladores e governo. Ele automatiza a coleta em diferentes fontes, aplica filtros de inteligência (IA) para relevância e gera arquivos de relatório prontos para uso.

## Principais funcionalidades

- Coleta automática de dados de várias fontes: ANEEL, EPE, MME, ONS, Petrobras, entre outras.
- Filtragem de notícias via IA (ex: relevância, escopo, categoria).
- Geração de relatório em PDF com layout personalizado.
- Organização automática de pastas (como `images/`, `relatorios/`) e versionamento via Git.

## Estrutura de pastas

```
botnoticias/
│  .env               ← variáveis de ambiente (chaves, credenciais)
│  config.py          ← arquivo de configuração geral
│  ia_filter.py       ← lógica de filtragem IA
│  save_pdf.py        ← rotina de salvamento/geração de PDF
│
├─ relatorios/        ← local onde os relatórios gerados são salvos
├─ images/            ← imagens associadas às notícias ou relatórios
└─ fontes específicas:
   ├─ coleta_aneel.py
   ├─ coleta_epe.py
   ├─ coleta_mme.py
   ├─ coleta_ons.py
   ├─ coleta_petrobras.py
   └─ coleta.py         ← coleta geral (agregadora)
```

## Pré‑requisitos

- Python 3.8 ou superior
- Instalar dependências via:

```bash
pip install -r requirements.txt
```

## Configuração

1. Crie um arquivo `.env` na raiz com as chaves/credenciais necessárias:
   ```dotenv
   API_KEY_XYZ=seu_valor
   OUTRAS_VAR=valor
   ```
2. Ajuste `config.py` conforme seu ambiente.
3. Verifique se as pastas `relatorios/` e `images/` existem.

## Uso

- Para executar a rotina de coleta geral:
  ```bash
  python coleta.py
  ```
- Para gerar um relatório PDF:
  ```bash
  python save_pdf.py
  ```
- Para executar um coletor específico (ex: ANEEL):
  ```bash
  python coleta_aneel.py
  ```

## Contribuição

Contribuições são bem‑vindas! Envie PRs, sugestões ou abra issues.
