# Videotonotes

Programma che monitora automaticamente una cartella di input, trascrive le registrazioni di videochiamate di lavoro con Whisper e genera riassunti strutturati con Ollama.

## Stack tecnico

| Componente | Tecnologia |
|---|---|
| File watcher | `watchdog` |
| Trascrizione audio | `openai-whisper` (modello `large-v3`) |
| Estrazione audio | `ffmpeg` (installato nel sistema) |
| Riassunto LLM | `ollama` + `llama3.1:8b` |
| Configurazione | `config.yaml` + variabili d'ambiente |
| Tracking file | `processed.json` |
| Logging | `logging` stdlib (log rotante) |
| Test | `pytest` |

## Struttura cartelle

```
videotonotes/
  input/               ← metti qui le registrazioni
  output/
    <nome_file>/
      transcript.md    ← trascrizione completa
      summary.md       ← riassunto strutturato
  logs/
    app.log            ← log rotante
  processed.json       ← tracking file elaborati
  config.yaml          ← configurazione
  src/
    logger.py
    tracker.py
    transcriber.py
    summarizer.py
    watcher.py
  tests/
    fixtures/
      sample.wav
    test_tracker.py
    test_transcriber.py
    test_summarizer.py
    test_watcher.py
  main.py
  requirements.txt
```

## Prerequisiti

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) installato e nel PATH
- [Ollama](https://ollama.com/) installato e in esecuzione

## Installazione

```bash
pip install -r requirements.txt
ollama pull llama3.1:8b
```

## Configurazione

Modifica `config.yaml` per cambiare percorsi, modelli o parametri. Tutte le chiavi supportano override tramite variabili d'ambiente (prefisso `VTN_`).

## Avvio

```bash
python main.py
```

All'avvio il programma esegue un health check automatico (ffmpeg, Ollama, modello) e segnala eventuali dipendenze mancanti.

Per fermare il programma e liberare la RAM: **Ctrl+C**. Lo stato viene salvato correttamente.

## Sviluppo

- **Test-oriented**: ogni modulo ha i suoi test in `tests/`. Aggiungere test prima o subito dopo aver scritto il codice.
- **Eseguire i test**: `pytest tests/`
- **Non procedere** alla fase successiva se i test falliscono.
- **Decisioni architetturali importanti**: chiedere input prima di implementare.

## Note Docker-readiness

Il progetto è strutturato per essere facilmente containerizzabile in futuro:
- Nessun percorso hardcoded (tutto in `config.yaml`)
- `ollama.base_url` configurabile tramite env var → punta al container Ollama
- `paths.*` configurabili → montabili come volumi Docker
- `.env.example` documenta le variabili d'ambiente necessarie
