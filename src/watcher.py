import os
import threading
import time
from typing import Callable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.logger import get_logger

logger = get_logger()


class VideoHandler(FileSystemEventHandler):
    def __init__(self, config: dict, tracker, on_stable_file: Callable[[str], None]):
        self._watcher_config = config.get("watcher", {})
        self._tracker = tracker
        self._on_stable_file = on_stable_file
        self._pending = set()
        self._pending_lock = threading.Lock()

    def _should_ignore(self, file_path: str) -> bool:
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()

        ignore_exts = self._watcher_config.get("ignore_extensions", [])
        if ext in ignore_exts:
            logger.debug(f"Ignorato (estensione temporanea): {filename}")
            return True

        ignore_prefixes = self._watcher_config.get("ignore_prefixes", [])
        if any(filename.startswith(p) for p in ignore_prefixes):
            logger.debug(f"Ignorato (prefisso): {filename}")
            return True

        supported = self._watcher_config.get("supported_extensions", [])
        if supported and ext not in supported:
            logger.debug(f"Ignorato (estensione non supportata): {filename}")
            return True

        return False

    def _enqueue(self, file_path: str):
        if self._should_ignore(file_path):
            return

        if self._tracker.is_processed(os.path.basename(file_path)):
            logger.debug(f"Già processato: {os.path.basename(file_path)}")
            return

        with self._pending_lock:
            if file_path in self._pending:
                return
            self._pending.add(file_path)

        logger.info(f"Nuovo file rilevato: {os.path.basename(file_path)}. Attendo stabilità...")
        thread = threading.Thread(
            target=self._wait_for_stability,
            args=(file_path,),
            daemon=True,
        )
        thread.start()

    def _wait_for_stability(self, file_path: str):
        wait_seconds = self._watcher_config.get("stability_wait_seconds", 10)
        poll_interval = 2
        stable_for = 0
        last_size = -1

        while stable_for < wait_seconds:
            try:
                size = os.path.getsize(file_path)
            except FileNotFoundError:
                logger.warning(f"File sparito durante attesa stabilità: {file_path}")
                with self._pending_lock:
                    self._pending.discard(file_path)
                return

            if size == last_size:
                stable_for += poll_interval
            else:
                stable_for = 0
                last_size = size

            time.sleep(poll_interval)

        with self._pending_lock:
            self._pending.discard(file_path)

        logger.info(f"File stabile, avvio elaborazione: {os.path.basename(file_path)}")
        self._on_stable_file(file_path)

    def on_created(self, event):
        if not event.is_directory:
            self._enqueue(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._enqueue(event.dest_path)


class VideoWatcher:
    def __init__(self, input_dir: str, config: dict, tracker, on_stable_file: Callable[[str], None]):
        self._input_dir = input_dir
        self._handler = VideoHandler(config, tracker, on_stable_file)
        self._observer = Observer()

    def start(self):
        self._observer.schedule(self._handler, self._input_dir, recursive=False)
        self._observer.start()
        logger.info(f"Watcher avviato su: {self._input_dir}")

    def stop(self):
        self._observer.stop()
        self._observer.join()
        logger.info("Watcher fermato.")
