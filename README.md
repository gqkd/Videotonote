# Videotonotes

Monitora automaticamente una cartella per nuove registrazioni di videochiamate, le trascrive con Whisper e genera riassunti strutturati con Ollama.

## Prerequisiti

- **Python 3.10+**
- **ffmpeg** — installalo e assicurati che sia nel PATH di sistema
  - Windows: [ffmpeg.org/download.html](https://ffmpeg.org/download.html) oppure `winget install ffmpeg`
- **Ollama** — [ollama.com](https://ollama.com/) (avvialo prima di eseguire il programma)

## Installazione

```bash
# Clona il repository
git clone <url-repo>
cd videotonotes

# Installa le dipendenze Python
pip install -r requirements.txt

# Scarica il modello Ollama (una volta sola)
ollama pull llama3.1:8b
```

> **Nota:** il modello Whisper `large-v3` (~3GB) viene scaricato automaticamente al primo avvio.

## Configurazione

Modifica `config.yaml` per personalizzare percorsi e modelli:

```yaml
paths:
  input: ./input       # cartella da monitorare
  output: ./output     # cartella dove salvare i risultati

whisper:
  model: large-v3      # modello di trascrizione
  language: it         # lingua principale

ollama:
  model: llama3.1:8b   # modello per i riassunti
```

Tutte le impostazioni possono essere sovrascritte tramite variabili d'ambiente (vedi `.env.example`).

## Avvio

```bash
python main.py
```

All'avvio il programma:
1. Verifica che ffmpeg e Ollama siano disponibili
2. Inizia a monitorare la cartella `input/`
3. Elabora automaticamente ogni nuovo file video

**Per fermare il programma e liberare la RAM:** premi `Ctrl+C`.

## Output

Per ogni file elaborato viene creata una sottocartella in `output/`:

```
output/
  nome_registrazione/
    transcript.md    ← trascrizione completa della chiamata
    summary.md       ← riassunto con punti chiave, decisioni e task
```

### Struttura di `summary.md`

```markdown
# Riassunto — nome_registrazione

## Riassunto generale
Breve descrizione dell'argomento principale della chiamata.

## Punti chiave discussi
- ...

## Decisioni prese
- ...

## Prossimi task
- ...
```

## Formati supportati

MKV, MP4, AVI, MOV, MP3, WAV

## Eseguire i test

```bash
pytest tests/
```

## Note Docker-readiness

Il progetto è pronto per essere containerizzato:
- Nessun percorso hardcoded (tutto in `config.yaml`)
- `ollama.base_url` configurabile via env var → punta al container Ollama
- Le cartelle `input/` e `output/` sono montabili come volumi Docker
- `.env.example` documenta tutte le variabili d'ambiente
