# Videotonotes

Automatically watches a folder for new call recordings, transcribes them with Whisper, and generates structured summaries with Ollama. Supports direct YouTube downloads.

## Requirements

- **Python 3.10+**
- **ffmpeg** — install it and make sure it's in your system PATH
  - Windows: [ffmpeg.org/download.html](https://ffmpeg.org/download.html) or `winget install ffmpeg`
- **Ollama** — [ollama.com](https://ollama.com/) (must be running before starting the program)

## Installation

```bash
# Clone the repository
git clone https://github.com/gqkd/Videotonote.git
cd Videotonote

# Install Python dependencies
pip install -r requirements.txt

# Pull the Ollama model (once)
ollama pull llama3.1:8b
```

> **Note:** the Whisper `large-v3` model (~3GB) is downloaded automatically on first run.

## Configuration

Edit `config.yaml` to customize paths, models, and behavior:

```yaml
whisper:
  model: large-v3
  language: null    # null = auto-detect (Italian, English, and others)
  device: auto      # auto | cpu | cuda

ollama:
  model: llama3.1:8b
  base_url: http://localhost:11434
```

All settings can be overridden with environment variables (see `.env.example`).

## Usage

```bash
python main.py
```

On startup the program:
1. Runs a health check (ffmpeg, Ollama, model availability)
2. Starts watching the `input/` folder
3. Automatically processes any new recording dropped in

**To stop the program and free RAM:** press `Ctrl+C`.

### YouTube download

Paste a YouTube URL directly into the running terminal:

```
> https://www.youtube.com/watch?v=...
```

Or from a second terminal:

```bash
python download.py https://www.youtube.com/watch?v=...
```

The audio is downloaded to `input/` and processed automatically by the watcher.

## Output

For each processed file a subfolder is created under `output/`:

```
output/
  recording_name/
    transcript.md    ← full transcription of the call
    summary.md       ← structured summary
```

### `summary.md` structure

```markdown
# Riassunto — recording_name

## Riassunto generale
Brief description of the main topic of the call.

## Punti chiave discussi
- ...

## Decisioni prese
- ...

## Prossimi task
- ...
```

## Supported formats

MKV, MP4, AVI, MOV, MP3, WAV

## Running tests

```bash
pytest tests/
```

Tests do not require Whisper, Ollama, or ffmpeg — everything is mocked.

## Docker-readiness

The project is structured for easy future containerization:
- No hardcoded paths (everything in `config.yaml`)
- `ollama.base_url` configurable via env var → point to an Ollama container
- `input/` and `output/` folders are ready to be mounted as Docker volumes
- `.env.example` documents all available environment variables
