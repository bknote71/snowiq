import threading
import time
from typing import Any, Optional


class DataCache:
    def __init__(self):
        self._store: dict[str, Any] = {}
        self._meta: dict[str, float] = {}
        self._lock = threading.Lock()

    def set(self, key: str, value: Any):
        with self._lock:
            self._store[key] = value
            self._meta[key] = time.time()

    def get(self, key: str, default=None):
        with self._lock:
            return self._store.get(key, default)

    def last_updated(self, key: str) -> Optional[float]:
        with self._lock:
            return self._meta.get(key)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._store)


cache = DataCache()
