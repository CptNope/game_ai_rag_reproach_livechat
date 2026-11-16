"""Shared state between the agent loop and the dashboard."""

import threading
import time
from collections import deque
from typing import Optional


class Session:
    def __init__(self):
        self.lock = threading.Lock()
        self.paused = False
        self.state: Optional[dict] = None
        self.situation = ""
        self.action = ""
        self.reason = ""
        self.memories: list = []
        self.think_ms = 0
        self.problem = ""
        self.memory_on = True
        self.score_series = deque(maxlen=300)
        self.x_series = deque(maxlen=300)
        self.events = deque(maxlen=200)
        self._event_id = 0
        self.frame: Optional[bytes] = None

    def event(self, text: str, kind: str = "info") -> None:
        with self.lock:
            self._event_id += 1
            self.events.append({"id": self._event_id, "time": time.strftime("%H:%M:%S"), "text": text, "kind": kind})

    def snapshot(self, since: int = 0) -> dict:
        with self.lock:
            return {
                "paused": self.paused,
                "state": self.state,
                "situation": self.situation,
                "action": self.action,
                "reason": self.reason,
                "memories": list(self.memories),
                "think_ms": self.think_ms,
                "problem": self.problem,
                "memory_on": self.memory_on,
                "score_series": list(self.score_series),
                "x_series": list(self.x_series),
                "events": [e for e in self.events if e["id"] > since],
                "has_frame": self.frame is not None,
            }
