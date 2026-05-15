import os
import time

from src.logger import get_logger

logger = get_logger()

# The prompt is intentionally in Italian to instruct the LLM to produce Italian output.
PROMPT_TEMPLATE = """Sei un assistente che analizza trascrizioni di videochiamate di lavoro.

Analizza la seguente trascrizione e produci un riassunto strutturato in italiano con queste sezioni:

1. **Riassunto generale**: un paragrafo che descrive l'argomento principale della chiamata.
2. **Punti chiave discussi**: elenco puntato dei temi principali trattati.
3. **Decisioni prese**: elenco puntato delle decisioni prese durante la chiamata (se nessuna, scrivi "Nessuna decisione formale presa.").
4. **Prossimi task**: elenco puntato delle azioni da fare emerse dalla chiamata (se nessuno, scrivi "Nessun task identificato.").

Rispondi SOLO con il contenuto delle sezioni, senza introduzioni o commenti aggiuntivi.
Usa questo formato esatto:

## Riassunto generale
[testo]

## Punti chiave discussi
- [punto]

## Decisioni prese
- [decisione]

## Prossimi task
- [task]

---
TRASCRIZIONE:
{transcript}
"""


def summarize(
    transcript_text: str,
    output_name: str,
    output_dir: str,
    ollama_config: dict,
) -> str:
    import ollama

    model = ollama_config.get("model", "llama3.1:8b")
    base_url = ollama_config.get("base_url", "http://localhost:11434")
    attempts = ollama_config.get("retry_attempts", 3)
    backoff = ollama_config.get("retry_backoff_seconds", [5, 15, 30])

    client = ollama.Client(host=base_url)
    prompt = PROMPT_TEMPLATE.format(transcript=transcript_text)

    last_error = None
    for attempt in range(attempts):
        try:
            logger.info(f"Requesting summary from Ollama (attempt {attempt + 1}/{attempts})...")
            response = client.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            summary_body = response["message"]["content"].strip()
            break
        except Exception as e:
            last_error = e
            logger.warning(f"Ollama unreachable: {e}")
            if attempt < attempts - 1:
                wait = backoff[attempt] if attempt < len(backoff) else backoff[-1]
                logger.info(f"Retrying in {wait}s...")
                time.sleep(wait)
    else:
        raise RuntimeError(
            f"Ollama did not respond after {attempts} attempts. Last error: {last_error}"
        )

    os.makedirs(output_dir, exist_ok=True)
    summary_path = os.path.join(output_dir, "summary.md")

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"# Riassunto — {output_name}\n\n")
        f.write(summary_body)
        f.write("\n")

    logger.info(f"Summary saved: {summary_path}")
    return summary_body
