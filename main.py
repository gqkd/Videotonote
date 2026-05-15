import os
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error

import yaml

from src.logger import setup_logger, get_logger
from src.tracker import Tracker
from src.transcriber import transcribe
from src.summarizer import summarize
from src.watcher import VideoWatcher
from src.downloader import download

# --- Config loading ---

ENV_OVERRIDES = {
    "VTN_PATHS_INPUT": ("paths", "input"),
    "VTN_PATHS_OUTPUT": ("paths", "output"),
    "VTN_PATHS_LOGS": ("paths", "logs"),
    "VTN_PATHS_PROCESSED_TRACKING": ("paths", "processed_tracking"),
    "VTN_WATCHER_STABILITY_WAIT_SECONDS": ("watcher", "stability_wait_seconds"),
    "VTN_WHISPER_MODEL": ("whisper", "model"),
    "VTN_WHISPER_LANGUAGE": ("whisper", "language"),
    "VTN_OLLAMA_BASE_URL": ("ollama", "base_url"),
    "VTN_OLLAMA_MODEL": ("ollama", "model"),
}


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    for env_var, (section, key) in ENV_OVERRIDES.items():
        value = os.environ.get(env_var)
        if value is not None:
            config.setdefault(section, {})[key] = value

    return config


def validate_config(config: dict):
    required = [
        ("paths", "input"),
        ("paths", "output"),
        ("paths", "logs"),
        ("paths", "processed_tracking"),
        ("whisper", "model"),
        ("ollama", "base_url"),
        ("ollama", "model"),
    ]
    for section, key in required:
        if not config.get(section, {}).get(key):
            raise ValueError(f"Missing config: [{section}] {key}")


# --- Health checks ---

def check_ffmpeg() -> bool:
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_ollama(base_url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base_url}/api/tags", timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def check_ollama_model(base_url: str, model_name: str) -> bool:
    import json
    try:
        with urllib.request.urlopen(f"{base_url}/api/tags", timeout=5) as resp:
            data = json.loads(resp.read())
            models = [m["name"] for m in data.get("models", [])]
            return any(model_name in m for m in models)
    except Exception:
        return False


def run_health_checks(config: dict) -> bool:
    logger = get_logger()
    ok = True

    if check_ffmpeg():
        logger.info("✓ ffmpeg found")
    else:
        logger.error("✗ ffmpeg not found. Install it and add it to PATH.")
        ok = False

    base_url = config["ollama"]["base_url"]
    if check_ollama(base_url):
        logger.info("✓ Ollama reachable")
    else:
        logger.error(f"✗ Ollama not reachable at {base_url}. Start Ollama before running the program.")
        ok = False

    model = config["ollama"]["model"]
    if ok and check_ollama_model(base_url, model):
        logger.info(f"✓ Ollama model '{model}' available")
    elif ok:
        logger.error(f"✗ Model '{model}' not found. Run: ollama pull {model}")
        ok = False

    return ok


# --- Processing ---

def process_file(file_path: str, config: dict, tracker: Tracker):
    logger = get_logger()
    filename = os.path.basename(file_path)
    output_name = os.path.splitext(filename)[0]
    output_dir = os.path.join(config["paths"]["output"], output_name)

    try:
        logger.info(f"Processing: {filename}")

        transcript_text = transcribe(file_path, output_dir, config["whisper"])
        summarize(transcript_text, output_name, output_dir, config["ollama"])

        tracker.mark_processed(filename, "success")
        logger.info(f"Done: {filename}")

    except KeyboardInterrupt:
        tracker.mark_processed(filename, "interrupted")
        logger.info(f"Processing interrupted: {filename}")
        raise

    except Exception as e:
        tracker.mark_processed(filename, "error")
        logger.error(f"Error processing {filename}: {e}", exc_info=True)


# --- URL input listener ---

def start_url_listener(input_dir: str):
    def listen():
        while True:
            try:
                line = input().strip()
            except EOFError:
                break
            if not line:
                continue
            if line.startswith("http://") or line.startswith("https://"):
                try:
                    download(line, input_dir)
                except Exception as e:
                    get_logger().error(f"Download error: {e}")
            else:
                get_logger().warning(f"Unrecognized input (expected a URL): {line}")

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()


# --- Main ---

def main():
    config = load_config()
    validate_config(config)

    setup_logger(config["paths"]["logs"])
    logger = get_logger()
    logger.info("=== Videotonotes started ===")

    os.makedirs(config["paths"]["input"], exist_ok=True)
    os.makedirs(config["paths"]["output"], exist_ok=True)

    if not run_health_checks(config):
        logger.error("Health check failed. Fix the issues above before starting.")
        sys.exit(1)

    tracker = Tracker(config["paths"]["processed_tracking"])

    def on_stable_file(file_path: str):
        process_file(file_path, config, tracker)

    watcher = VideoWatcher(config["paths"]["input"], config, tracker, on_stable_file)
    watcher.start()

    start_url_listener(config["paths"]["input"])

    logger.info(f"Watching: {config['paths']['input']}")
    logger.info("Paste a YouTube URL to download and process it automatically.")
    logger.info("Press Ctrl+C to stop the program and free RAM.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        watcher.stop()
        logger.info("=== Videotonotes stopped ===")


if __name__ == "__main__":
    main()
