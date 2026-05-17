# Videotonotes

Programma che monitora automaticamente una cartella di input, trascrive registrazioni di videochiamate con Whisper e genera riassunti strutturati con Ollama. Supporta anche il download diretto da YouTube.

## Stato attuale (MVP completo)

Tutte le fasi del piano originale sono state completate e testate. 28 test unitari verdi.

## Stack tecnico

| Componente | Tecnologia | Note |
|---|---|---|
| File watcher | `watchdog` | Monitora `input/`, filtra temporanei |
| Trascrizione | `openai-whisper large-v3` | GPU auto-detect (CUDA se disponibile, altrimenti CPU) |
| Audio extraction | `ffmpeg` (system) | Gestisce MKV, MP4, MP3, WAV, ecc. |
| Riassunto | `ollama` + modello configurabile | Default: `llama3.1:8b`, retry 3x |
| Download YouTube | `yt-dlp` | Via `download.py` o URL inline nel terminale |
| Configurazione | `config.yaml` + env vars | Docker-ready |
| Tracking | `processed.json` | JSON leggero, evita riprocessamento |
| Logging | `logging` stdlib | Log rotante in `logs/app.log` |
| Test | `pytest` | 28 test unitari, tutti mockati (no dipendenze esterne) |

## Struttura progetto

```
videotonotes/
  input/               ← registrazioni da processare (gitignored)
  output/
    <nome_file>/
      transcript.md    ← trascrizione completa
      summary.md       ← riassunto strutturato
  logs/
    app.log            ← log rotante (gitignored)
  processed.json       ← tracking file elaborati (gitignored)
  config.yaml          ← configurazione principale
  main.py              ← entry point (watcher + URL listener)
  download.py          ← CLI per scaricare da YouTube
  src/
    logger.py          ← setup logging rotante
    tracker.py         ← gestione processed.json (thread-safe)
    transcriber.py     ← Whisper: load/unload per file, GPU auto-detect
    summarizer.py      ← Ollama: prompt italiano, retry esponenziale
    watcher.py         ← watchdog + stability check (10s)
    downloader.py      ← yt-dlp download YouTube
  tests/
    fixtures/
      sample.wav       ← audio breve per test (1s di silenzio)
    test_tracker.py    ← 7 test
    test_transcriber.py← 8 test (whisper e torch mockati)
    test_summarizer.py ← 5 test (ollama mockato)
    test_watcher.py    ← 8 test
```

## Avvio

```bash
pip install -r requirements.txt
ollama pull llama3.1:8b   # prima volta
python main.py
```

## Comandi disponibili a runtime

Con `main.py` in esecuzione:
- **Incolla un URL YouTube** direttamente nel terminale → scarica in `input/` e processa automaticamente
- **Ctrl+C** → shutdown pulito, RAM liberata

Da un secondo terminale:
```bash
python download.py https://www.youtube.com/watch?v=...
```

## config.yaml — opzioni chiave

```yaml
whisper:
  model: large-v3
  language: null    # null = auto-detect italiano/inglese/altro
  device: auto      # auto | cpu | cuda

ollama:
  base_url: http://localhost:11434
  model: llama3.1:8b         # cambiare con modello disponibile
  retry_attempts: 3
  retry_backoff_seconds: [5, 15, 30]
```

**Override via env vars** (Docker-ready): `VTN_OLLAMA_BASE_URL`, `VTN_WHISPER_MODEL`, ecc. — vedi `.env.example`.

## Comportamenti importanti da sapere

- **Whisper**: caricato e scaricato dalla RAM ad ogni file (load/unload per file). Lento ma libera memoria tra un job e l'altro.
- **GPU**: se CUDA è disponibile, Whisper la usa automaticamente. Ollama gestisce la GPU da solo.
- **File temporanei**: il watcher ignora `.tmp`, `.part`, `.crdownload` e file che iniziano con `~`, `.`, `_`.
- **Stabilità**: il watcher aspetta 10 secondi senza modifiche al file prima di elaborarlo (gestisce i file temporanei dei software di registrazione).
- **Tracker**: solo i file con `status: success` in `processed.json` vengono ignorati al prossimo avvio. File con `status: error` o `interrupted` vengono rielaborati automaticamente al prossimo avvio; il record viene aggiornato in-place (non duplicato).
- **Lingua**: Whisper rileva la lingua automaticamente (non forzare `language: it` — degrada la qualità su audio inglese).

## Eseguire i test

```bash
pytest tests/          # tutti i test
pytest tests/ -v       # con dettaglio
pytest tests/test_transcriber.py  # modulo specifico
```

I test non richiedono Whisper, Ollama o ffmpeg installati — tutto è mockato.

## Prerequisiti sistema

- Python 3.10+
- ffmpeg nel PATH (`winget install ffmpeg` su Windows)
- Ollama in esecuzione (`ollama serve`)

## Architettura — flusso principale

```
input/<file>
    ↓
[Watcher] filtra temporanei + controlla tracker
    ↓
[Stability check] aspetta 10s senza modifiche
    ↓
[Transcriber] Whisper large-v3 → output/<nome>/transcript.md
    ↓
[Summarizer] Ollama → output/<nome>/summary.md
    ↓
[Tracker] segna "success" in processed.json
```

## Docker-readiness (futura)

Il progetto è già strutturato per Docker:
- Nessun percorso hardcoded (tutto in `config.yaml`)
- `ollama.base_url` configurabile → punterà al container Ollama
- `paths.*` → volumi Docker
- `.env.example` documenta le variabili d'ambiente

Per containerizzare: creare `Dockerfile` + `docker-compose.yml` con due servizi (app + ollama) e montare `input/` e `output/` come volumi.

## Idee per sviluppi futuri

- Containerizzazione Docker + docker-compose
- Interfaccia web minimale per visualizzare riassunti
- Notifiche (email, Slack) al termine dell'elaborazione
- Supporto multi-speaker nella trascrizione
- Esportazione riassunti in PDF o DOCX
