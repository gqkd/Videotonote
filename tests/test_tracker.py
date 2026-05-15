import os
import pytest
from src.tracker import Tracker


@pytest.fixture
def tracker(tmp_path):
    return Tracker(str(tmp_path / "processed.json"))


def test_new_file_not_processed(tracker):
    assert tracker.is_processed("video.mkv") is False


def test_mark_success_makes_processed(tracker):
    tracker.mark_processed("video.mkv", "success")
    assert tracker.is_processed("video.mkv") is True


def test_mark_error_not_considered_processed(tracker):
    tracker.mark_processed("video.mkv", "error")
    assert tracker.is_processed("video.mkv") is False


def test_persistence(tmp_path):
    path = str(tmp_path / "processed.json")
    t1 = Tracker(path)
    t1.mark_processed("video.mkv", "success")

    t2 = Tracker(path)
    assert t2.is_processed("video.mkv") is True


def test_mark_interrupted_not_considered_processed(tracker):
    tracker.mark_processed("video.mkv", "interrupted")
    assert tracker.is_processed("video.mkv") is False


def test_multiple_files(tracker):
    tracker.mark_processed("a.mkv", "success")
    tracker.mark_processed("b.mkv", "error")
    assert tracker.is_processed("a.mkv") is True
    assert tracker.is_processed("b.mkv") is False
    assert tracker.is_processed("c.mkv") is False
