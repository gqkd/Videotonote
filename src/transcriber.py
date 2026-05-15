import gc
import os

from src.logger import get_logger

logger = get_logger()


def _select_device(requested: str) -> str:
    import torch

    if requested and requested.lower() != "auto":
        return requested.lower()

    if torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        logger.info(f"GPU detected: {name} — Whisper will run on CUDA.")
        return "cuda"

    logger.info("No CUDA GPU detected — Whisper will run on CPU.")
    return "cpu"


def transcribe(file_path: str, output_dir: str, whisper_config: dict) -> str:
    import whisper

    model_name = whisper_config.get("model", "large-v3")
    language = whisper_config.get("language", None)
    device = _select_device(whisper_config.get("device", "auto"))

    logger.info(f"Loading Whisper model '{model_name}' on {device.upper()}...")
    model = whisper.load_model(model_name, device=device)

    lang_display = language if language else "auto-detect"
    logger.info(f"Transcribing: {os.path.basename(file_path)} (language: {lang_display})")
    result = model.transcribe(file_path, language=language or None, verbose=True)

    transcript_text = result["text"].strip()

    del model
    gc.collect()
    logger.info("Whisper model unloaded from RAM.")

    os.makedirs(output_dir, exist_ok=True)
    output_name = os.path.basename(output_dir)
    transcript_path = os.path.join(output_dir, "transcript.md")

    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(f"# Trascrizione — {output_name}\n\n")
        f.write(transcript_text)
        f.write("\n")

    logger.info(f"Transcript saved: {transcript_path}")
    return transcript_text
