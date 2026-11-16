import json

from mario_ai import brain as brain_mod
from mario_ai.brain import Brain, OllamaError, parse_decision


class Reply:
    def __init__(self, status, body):
        self.status_code = status
        self._body = body

    def json(self):
        return self._body


def test_parse_valid_decision():
    assert parse_decision('{"action": "jump_right", "reason": "Goomba ahead."}') == ("jump_right", "Goomba ahead.")


def test_parse_bad_replies_fall_back_to_moving_right():
    assert parse_decision("not json")[0] == "run_right"
    assert parse_decision('{"action": "fly", "reason": "x"}')[0] == "run_right"


def test_decide_sends_schema_and_memories(monkeypatch):
    sent = {}

    def fake_post(url, json=None, timeout=None):
        sent.update(url=url, body=json)
        return Reply(200, {"message": {"content": '{"action": "jump", "reason": "Enemy close."}'}})

    monkeypatch.setattr(brain_mod.requests, "post", fake_post)
    b = Brain("http://ollama", "llama3.2")
    action, reason = b.decide("An enemy is right in front of Mario.", [{"situation": "s", "action": "right", "outcome": "Mario lost a life"}])
    assert (action, reason) == ("jump", "Enemy close.")
    assert sent["url"] == "http://ollama/api/chat"
    assert sent["body"]["format"]["properties"]["action"]["enum"][0] == "right"
    assert "Mario lost a life" in sent["body"]["messages"][1]["content"]


def test_missing_model_message(monkeypatch):
    monkeypatch.setattr(brain_mod.requests, "post", lambda *a, **k: Reply(404, {}))
    try:
        Brain("http://ollama", "llama3.2").decide("x", [])
    except OllamaError as exc:
        assert "ollama pull llama3.2" in str(exc)
    else:
        raise AssertionError("expected OllamaError")
