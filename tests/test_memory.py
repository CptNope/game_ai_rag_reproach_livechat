from mario_ai import memory as memory_mod
from mario_ai.memory import Memory, cosine


def test_cosine():
    assert round(cosine([1, 0], [1, 0]), 3) == 1.0
    assert round(cosine([1, 0], [0, 1]), 3) == 0.0


def test_remember_and_recall_most_similar(tmp_path):
    m = Memory(str(tmp_path / "memory.jsonl"), "http://ollama", "nomic-embed-text")
    m.remember("enemy ahead", "jump", "moved +40 px", [1.0, 0.0])
    m.remember("open ground", "run_right", "moved +60 px", [0.0, 1.0])
    best = m.recall([0.9, 0.1], top_k=1)
    assert best == [{"situation": "enemy ahead", "action": "jump", "outcome": "moved +40 px"}]
    # Survives a restart.
    again = Memory(str(tmp_path / "memory.jsonl"), "http://ollama", "nomic-embed-text")
    assert len(again.items) == 2


def test_embedding_failure_turns_memory_off(tmp_path, monkeypatch):
    import requests

    def down(*a, **k):
        raise requests.ConnectionError()

    monkeypatch.setattr(memory_mod.requests, "post", down)
    m = Memory(str(tmp_path / "m.jsonl"), "http://ollama", "nomic-embed-text")
    assert m.embed("x") is None
    assert m.available is False
