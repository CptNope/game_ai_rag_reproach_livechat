"""Ask a local model in Ollama for the next move, as structured JSON."""

import json
from typing import List, Tuple

import requests

from .controller import ACTIONS

SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": list(ACTIONS)},
        "reason": {"type": "string"},
    },
    "required": ["action", "reason"],
}

SYSTEM = (
    "You control Mario in Super Mario Bros. Your goal is to move right through the level "
    "without dying. Jump over enemies and gaps, and use past experience when it is given. "
    "Reply only with JSON: an action from the list and a one-sentence reason. Actions: "
    + ", ".join(ACTIONS)
    + "."
)


class OllamaError(RuntimeError):
    pass


class Brain:
    def __init__(self, ollama_url: str, model: str, timeout: float = 60):
        self.url = ollama_url
        self.model = model
        self.timeout = timeout

    def build_prompt(self, situation: str, memories: List[dict]) -> str:
        lines = ["Current situation: " + situation]
        if memories:
            lines.append("Similar past situations and what happened:")
            for m in memories:
                lines.append("- %s -> did %s, %s" % (m["situation"], m["action"], m["outcome"]))
        lines.append("What should Mario do next?")
        return "\n".join(lines)

    def decide(self, situation: str, memories: List[dict]) -> Tuple[str, str]:
        try:
            reply = requests.post(
                self.url + "/api/chat",
                json={
                    "model": self.model,
                    "stream": False,
                    "format": SCHEMA,
                    "options": {"temperature": 0.2},
                    "messages": [
                        {"role": "system", "content": SYSTEM},
                        {"role": "user", "content": self.build_prompt(situation, memories)},
                    ],
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise OllamaError("Can't reach Ollama at %s." % self.url) from exc
        if reply.status_code == 404:
            raise OllamaError("Model %s isn't installed. Run `ollama pull %s`." % (self.model, self.model))
        if reply.status_code != 200:
            raise OllamaError("Ollama returned an error (%d)." % reply.status_code)
        return parse_decision(reply.json().get("message", {}).get("content", ""))


def parse_decision(text: str) -> Tuple[str, str]:
    """Read the model's JSON. Anything unusable becomes a safe default move."""
    try:
        data = json.loads(text)
        action = str(data.get("action", "")).strip()
        reason = str(data.get("reason", "")).strip()[:200]
    except (ValueError, AttributeError):
        return "run_right", "Couldn't read the model's reply, so Mario keeps moving."
    if action not in ACTIONS:
        return "run_right", "The model chose an unknown move (%s), so Mario keeps moving." % action[:30]
    return action, reason or "No reason given."
