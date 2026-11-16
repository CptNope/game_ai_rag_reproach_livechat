from fakes import FakeGame

from mario_ai.agent import Agent
from mario_ai.config import Config
from mario_ai.controller import KeyboardController
from mario_ai.dashboard import create_app
from mario_ai.memory import Memory
from mario_ai.session import Session


class FixedBrain:
    def __init__(self, action="run_jump_right"):
        self.action = action

    def decide(self, situation, memories):
        return self.action, "Testing."


class OfflineMemory(Memory):
    def embed(self, text):
        return [float(len(text)), 1.0]


def make_agent(tmp_path, game):
    cfg = Config()
    cfg.data_dir = str(tmp_path)
    cfg.hold_time = 0
    cfg.step_delay = 0
    return Agent(
        cfg, Session(), retroarch=game, brain=FixedBrain(),
        memory=OfflineMemory(str(tmp_path / "memory.jsonl"), "http://x", "e"),
        controller=KeyboardController(backend=game),
    )


def test_step_moves_mario_learns_and_pauses_while_thinking(tmp_path):
    game = FakeGame()
    agent = make_agent(tmp_path, game)
    assert agent.step()
    snap = agent.session.snapshot()
    assert snap["action"] == "run_jump_right"
    assert snap["state"]["x"] == 64
    assert snap["score_series"] == [100]
    assert game.commands.count("PAUSE_TOGGLE") == 2 and not game.paused
    assert agent.memory.items[0]["outcome"] == "moved +24 px and scored 100"
    assert (tmp_path / "decisions.jsonl").exists()


def test_dashboard_state_and_controls(tmp_path):
    game = FakeGame()
    agent = make_agent(tmp_path, game)
    agent.step()
    client = create_app(agent).test_client()
    assert client.get("/").status_code == 200
    data = client.get("/api/state").get_json()
    assert data["state"]["stage"] == "1-1"
    assert data["stats"]["decisions"] == 1
    assert client.post("/api/control", json={"action": "pause"}).get_json()["paused"] is True
    assert client.post("/api/control", json={"action": "save_state"}).status_code == 200
    assert "SAVE_STATE" in game.commands
    assert client.post("/api/control", json={"action": "format_disk"}).status_code == 400
    export = client.get("/api/export")
    assert export.status_code == 200 and export.mimetype == "application/zip"
    assert client.get("/frame.jpg").status_code == 204


def test_changes_between_moves_are_still_counted(tmp_path):
    from mario_ai import game_state as gs

    game = FakeGame()
    agent = make_agent(tmp_path, game)
    agent.step()
    game.ram[gs.LEVEL] = 1  # level changes while no move is in progress
    agent.step()
    stats = agent.tracker.stats
    assert stats["levels_cleared"] == 1
    assert stats["completions"]["1-1"] == 1
