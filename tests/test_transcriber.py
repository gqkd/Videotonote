import os
import sys
import pytest
from unittest.mock import MagicMock, patch


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_WAV = os.path.join(FIXTURES_DIR, "sample.wav")

WHISPER_CONFIG = {"model": "large-v3", "language": "it"}
FAKE_TRANSCRIPT = "Ciao, questa è una trascrizione di test."


@pytest.fixture
def mock_whisper():
    mock_module = MagicMock()
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": FAKE_TRANSCRIPT}
    mock_module.load_model.return_value = mock_model

    with patch.dict(sys.modules, {"whisper": mock_module}):
        yield mock_module, mock_model


def test_transcript_md_created(tmp_path, mock_whisper):
    from src.transcriber import transcribe

    output_dir = str(tmp_path / "video_test")
    transcribe(SAMPLE_WAV, output_dir, WHISPER_CONFIG)

    assert os.path.exists(os.path.join(output_dir, "transcript.md"))


def test_transcript_md_header(tmp_path, mock_whisper):
    from src.transcriber import transcribe

    output_dir = str(tmp_path / "video_test")
    transcribe(SAMPLE_WAV, output_dir, WHISPER_CONFIG)

    with open(os.path.join(output_dir, "transcript.md"), encoding="utf-8") as f:
        content = f.read()

    assert content.startswith("# Trascrizione — video_test")


def test_transcript_md_content(tmp_path, mock_whisper):
    from src.transcriber import transcribe

    output_dir = str(tmp_path / "video_test")
    result = transcribe(SAMPLE_WAV, output_dir, WHISPER_CONFIG)

    assert result == FAKE_TRANSCRIPT

    with open(os.path.join(output_dir, "transcript.md"), encoding="utf-8") as f:
        content = f.read()

    assert FAKE_TRANSCRIPT in content


def test_whisper_model_loaded_with_correct_name(tmp_path, mock_whisper):
    from src.transcriber import transcribe

    mock_module, _ = mock_whisper
    output_dir = str(tmp_path / "video_test")
    transcribe(SAMPLE_WAV, output_dir, WHISPER_CONFIG)

    mock_module.load_model.assert_called_once_with("large-v3")


def test_output_dir_created_if_missing(tmp_path, mock_whisper):
    from src.transcriber import transcribe

    output_dir = str(tmp_path / "nested" / "video_test")
    assert not os.path.exists(output_dir)

    transcribe(SAMPLE_WAV, output_dir, WHISPER_CONFIG)

    assert os.path.isdir(output_dir)
