import json
import os
import threading
from datetime import datetime


class Tracker:
    def __init__(self, tracking_path: str):
        self._path = tracking_path
        self._lock = threading.Lock()
        self._data = self._load()

    def _load(self) -> dict:
        if not os.path.exists(self._path):
            return {"processed": []}
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def is_processed(self, filename: str) -> bool:
        with self._lock:
            return any(
                entry["file"] == filename and entry["status"] == "success"
                for entry in self._data["processed"]
            )

    def mark_processed(self, filename: str, status: str):
        with self._lock:
            entry = next(
                (e for e in self._data["processed"] if e["file"] == filename),
                None,
            )
            now = datetime.now().isoformat(timespec="seconds")
            if entry is not None:
                entry["status"] = status
                entry["processed_at"] = now
            else:
                self._data["processed"].append(
                    {"file": filename, "processed_at": now, "status": status}
                )
            self._save()
