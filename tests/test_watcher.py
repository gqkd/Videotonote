import os
import pytest
from unittest.mock import MagicMock, patch

CONFIG = {
    "watcher": {
        "stability_wait_seconds": 10,
        "supported_extensions": [".mkv", ".mp4", ".avi", ".mov", ".mp3", ".wav"],
        "ignore_prefixes": ["~", ".", "_"],
        "ignore_extensions": [".tmp", ".part", ".crdownload"],
    }
}


def make_handler(is_processed=False, callback=None):
    from src.watcher import VideoHandler

    tracker = MagicMock()
    tracker.is_processed.return_value = is_processed

    cb = callback or MagicMock()
    handler = VideoHandler(CONFIG, tracker, cb)
    return handler, tracker, cb


def test_ignore_tmp_extension():
    handler, _, cb = make_handler()
    with patch.object(handler, "_wait_for_stability") as mock_wait:
        handler._enqueue("/input/video.tmp")
        mock_wait.assert_not_called()


def test_ignore_part_extension():
    handler, _, cb = make_handler()
    with patch.object(handler, "_wait_for_stability") as mock_wait:
        handler._enqueue("/input/video.part")
        mock_wait.assert_not_called()


def test_ignore_tilde_prefix():
    handler, _, cb = make_handler()
    with patch.object(handler, "_wait_for_stability") as mock_wait:
        handler._enqueue("/input/~video.mkv")
        mock_wait.assert_not_called()


def test_ignore_dot_prefix():
    handler, _, cb = make_handler()
    with patch.object(handler, "_wait_for_stability") as mock_wait:
        handler._enqueue("/input/.video.mkv")
        mock_wait.assert_not_called()


def test_ignore_unsupported_extension():
    handler, _, cb = make_handler()
    with patch.object(handler, "_wait_for_stability") as mock_wait:
        handler._enqueue("/input/video.xyz")
        mock_wait.assert_not_called()


def test_ignore_already_processed():
    handler, tracker, cb = make_handler(is_processed=True)
    with patch.object(handler, "_wait_for_stability") as mock_wait:
        handler._enqueue("/input/video.mkv")
        mock_wait.assert_not_called()


def test_valid_file_enqueued():
    handler, _, cb = make_handler()
    with patch.object(handler, "_wait_for_stability") as mock_wait:
        with patch("threading.Thread") as mock_thread:
            mock_thread.return_value.start = MagicMock()
            handler._enqueue("/input/video.mkv")
            mock_thread.assert_called_once()


def test_duplicate_not_enqueued_twice():
    handler, _, cb = make_handler()
    with patch.object(handler, "_wait_for_stability"):
        with patch("threading.Thread") as mock_thread:
            mock_thread.return_value.start = MagicMock()
            handler._enqueue("/input/video.mkv")
            handler._enqueue("/input/video.mkv")
            assert mock_thread.call_count == 1
