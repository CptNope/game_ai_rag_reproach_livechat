"""The play loop: read the game, recall similar moments, ask the model, press buttons, learn."""

import io
import json
import os
import threading
import time

from .brain import Brain, OllamaError
from .config import Config
from .controller import KeyboardController
from .game_state import read_state
from .memory import Memory
from .retroarch import RetroArch, RetroArchError
from .session import Session
from .tracker import Tracker


class Agent:
    def __init__(self, config: Config, session: Session, retroarch=None, brain=None, memory=None, controller=None, tracker=None):
        self.config = config
        self.session = session
        self.retroarch = retroarch or RetroArch(config.retroarch_host, config.retroarch_port)
        self.brain = brain or Brain(config.ollama_url, config.model)
        self.memory = memory or Memory(os.path.join(config.data_dir, "memory.jsonl"), config.ollama_url, config.embed_model)
        self.controller = controller or KeyboardController()
        self.tracker = tracker or Tracker(config.data_dir)
        self.decisions_path = os.path.join(config.data_dir, "decisions.jsonl")
        self._stop = threading.Event()
        self._started = False
        self._last = None  # last state seen, so changes between moves still count

    def stop(self) -> None:
        self._stop.set()

    def _problem(self, text: str) -> None:
        if self.session.problem != text:
            self.session.problem = text
            if text:
                self.session.event(text, "problem")

    def _set_paused(self, paused: bool) -> None:
        try:
            status = self.retroarch.status()
        except RetroArchError:
            return
        if (paused and status == "PLAYING") or (not paused and status == "PAUSED"):
            self.retroarch.command("PAUSE_TOGGLE")

    def step(self) -> bool:
        """One decision. Returns False when it couldn't play (the reason is on the dashboard)."""
        cfg = self.config
        try:
            before = read_state(self.retroarch.read_memory)
        except RetroArchError as exc:
            self._problem(str(exc))
            return False

        if not self._started:
            self.tracker.start(before)
            self._started = True
            self.session.event("Started playing %s." % before.stage)

        situation = before.describe()
        if cfg.think_paused:
            self._set_paused(True)
        started = time.monotonic()
        vector = self.memory.embed(situation)
        memories = self.memory.recall(vector)
        try:
            action, reason = self.brain.decide(situation, memories)
        except OllamaError as exc:
            self._problem(str(exc))
            if cfg.think_paused:
                self._set_paused(False)
            return False
        think_ms = int((time.monotonic() - started) * 1000)
        if cfg.think_paused:
            self._set_paused(False)

        self.controller.perform(action, cfg.hold_time)

        try:
            after = read_state(self.retroarch.read_memory)
        except RetroArchError as exc:
            self._problem(str(exc))
            return False
        self._problem("")

        outcome = Tracker.outcome(before, after)
        self.memory.remember(situation, action, outcome, vector)
        # Compare with the last state seen, not just this move's start, so a level
        # change or lost life that happened between moves is still counted.
        events = self.tracker.update(self._last or before, after)
        self._last = after

        os.makedirs(cfg.data_dir, exist_ok=True)
        with open(self.decisions_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"time": time.time(), "situation": situation, "action": action, "reason": reason, "outcome": outcome}) + "\n")

        s = self.session
        with s.lock:
            s.state = after.to_dict()
            s.situation = situation
            s.action = action
            s.reason = reason
            s.memories = memories
            s.think_ms = think_ms
            s.memory_on = self.memory.available
            s.score_series.append(after.score)
            s.x_series.append(after.x)
        for text in events:
            s.event(text, "achievement" if text.startswith("Achievement:") else "game")
        if cfg.capture_frames:
            self._capture()
        return True

    def _capture(self) -> None:
        try:
            import mss
            from PIL import Image

            with mss.mss() as sct:
                shot = sct.grab(sct.monitors[1])
            img = Image.frombytes("RGB", shot.size, shot.rgb)
            img.thumbnail((640, 480))
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=70)
            self.session.frame = buf.getvalue()
        except Exception:  # Optional feature: never stop play over a screenshot.
            self.session.frame = None

    def run(self) -> None:
        while not self._stop.is_set():
            if self.session.paused:
                time.sleep(0.2)
                continue
            ok = self.step()
            time.sleep(self.config.step_delay if ok else 2.0)
