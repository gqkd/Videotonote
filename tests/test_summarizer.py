import os
import sys
import pytest
from unittest.mock import MagicMock, patch

OLLAMA_CONFIG = {
    "model": "llama3.1:8b",
    "base_url": "http://localhost:11434",
    "retry_attempts": 3,
    "retry_backoff_seconds": [0, 0, 0],
}

FAKE_TRANSCRIPT = "Abbiamo discusso del progetto X e deciso di procedere."

FAKE_SUMMARY_BODY = """## Riassunto generale
La chiamata riguardava il progetto X.

## Punti chiave discussi
- Avanzamento del progetto X

## Decisioni prese
- Procedere con l'implementazione

## Prossimi task
- Completare il modulo entro venerdì"""


def make_mock_ollama(response_content=FAKE_SUMMARY_BODY, fail_times=0):
    mock_module = MagicMock()
    mock_client = MagicMock()
    mock_module.Client.return_value = mock_client

    call_count = {"n": 0}

    def chat_side_effect(**kwargs):
        call_count["n"] += 1
        if call_count["n"] <= fail_times:
            raise ConnectionError("Ollama non raggiungibile")
        return {"message": {"content": response_content}}

    mock_client.chat.side_effect = chat_side_effect
    return mock_module, mock_client


def test_summary_md_created(tmp_path):
    mock_module, _ = make_mock_ollama()
    with patch.dict(sys.modules, {"ollama": mock_module}):
        from src.summarizer import summarize
        output_dir = str(tmp_path / "video_test")
        summarize(FAKE_TRANSCRIPT, "video_test", output_dir, OLLAMA_CONFIG)

    assert os.path.exists(os.path.join(output_dir, "summary.md"))


def test_summary_md_header(tmp_path):
    mock_module, _ = make_mock_ollama()
    with patch.dict(sys.modules, {"ollama": mock_module}):
        from src.summarizer import summarize
        output_dir = str(tmp_path / "video_test")
        summarize(FAKE_TRANSCRIPT, "video_test", output_dir, OLLAMA_CONFIG)

    with open(os.path.join(output_dir, "summary.md"), encoding="utf-8") as f:
        content = f.read()

    assert content.startswith("# Riassunto — video_test")


def test_summary_md_four_sections(tmp_path):
    mock_module, _ = make_mock_ollama()
    with patch.dict(sys.modules, {"ollama": mock_module}):
        from src.summarizer import summarize
        output_dir = str(tmp_path / "video_test")
        summarize(FAKE_TRANSCRIPT, "video_test", output_dir, OLLAMA_CONFIG)

    with open(os.path.join(output_dir, "summary.md"), encoding="utf-8") as f:
        content = f.read()

    assert "## Riassunto generale" in content
    assert "## Punti chiave discussi" in content
    assert "## Decisioni prese" in content
    assert "## Prossimi task" in content


def test_retry_on_failure(tmp_path):
    mock_module, mock_client = make_mock_ollama(fail_times=2)
    with patch.dict(sys.modules, {"ollama": mock_module}):
        from src.summarizer import summarize
        output_dir = str(tmp_path / "video_test")
        summarize(FAKE_TRANSCRIPT, "video_test", output_dir, OLLAMA_CONFIG)

    assert mock_client.chat.call_count == 3


def test_raises_after_max_retries(tmp_path):
    mock_module, _ = make_mock_ollama(fail_times=10)
    with patch.dict(sys.modules, {"ollama": mock_module}):
        from src.summarizer import summarize
        output_dir = str(tmp_path / "video_test")
        with pytest.raises(RuntimeError, match="Ollama non ha risposto"):
            summarize(FAKE_TRANSCRIPT, "video_test", output_dir, OLLAMA_CONFIG)
