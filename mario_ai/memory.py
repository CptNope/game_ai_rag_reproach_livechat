"""Retrieval-augmented memory: remember situations and what happened after each move.

Each experience is embedded with an Ollama embedding model and kept in a
JSON Lines file. Before each decision, the most similar past situations
are retrieved and given to the model as context.
"""

import json
import math
import os
from typing import List, Optional

import requests


class Memory:
    def __init__(self, path: str, ollama_url: str, embed_model: str, timeout: float = 30):
        self.path = path
        self.url = ollama_url
        self.model = embed_model
        self.timeout = timeout
        self.items: List[dict] = []
        self.available = True
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            self.items.append(json.loads(line))
                        except ValueError:
                            continue

    def embed(self, text: str) -> Optional[List[float]]:
        if not self.available:
            return None
        try:
            reply = requests.post(self.url + "/api/embed", json={"model": self.model, "input": text}, timeout=self.timeout)
            reply.raise_for_status()
            vectors = reply.json().get("embeddings") or []
            return vectors[0] if vectors else None
        except (requests.RequestException, ValueError):
            # Keep playing without memory; the dashboard shows why.
            self.available = False
            return None

    def remember(self, situation: str, action: str, outcome: str, vector: Optional[List[float]]) -> None:
        if vector is None:
            return
        item = {"situation": situation, "action": action, "outcome": outcome, "vector": vector}
        self.items.append(item)
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(item) + "\n")

    def recall(self, vector: Optional[List[float]], top_k: int = 3) -> List[dict]:
        if vector is None or not self.items:
            return []
        scored = sorted(self.items, key=lambda item: cosine(vector, item["vector"]), reverse=True)
        return [{k: v for k, v in item.items() if k != "vector"} for item in scored[:top_k]]


def cosine(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        return -1.0
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else -1.0
