import gc
import os

from src.logger import get_logger

logger = get_logger()


def transcribe(file_path: str, output_dir: str, whisper_config: dict) -> str:
    import whisper

    model_name = whisper_config.get("model", "large-v3")
    language = whisper_config.get("language", "it")

    logger.info(f"Caricamento modello Whisper '{model_name}'...")
    model = whisper.load_model(model_name)

    logger.info(f"Trascrizione in corso: {os.path.basename(file_path)}")
    result = model.transcribe(file_path, language=language, verbose=True)

    transcript_text = result["text"].strip()

    del model
    gc.collect()
    logger.info("Modello Whisper scaricato dalla RAM.")

    os.makedirs(output_dir, exist_ok=True)
    output_name = os.path.basename(output_dir)
    transcript_path = os.path.join(output_dir, "transcript.md")

    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(f"# Trascrizione — {output_name}\n\n")
        f.write(transcript_text)
        f.write("\n")

    logger.info(f"Trascrizione salvata: {transcript_path}")
    return transcript_text
