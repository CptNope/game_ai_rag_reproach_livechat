"""Achievements and stats, worked out by comparing game states before and after each move."""

import json
import os
from typing import List, Optional

from .game_state import GameState

ACHIEVEMENTS = {
    "mushroom": "Got a Super Mushroom",
    "fire": "Got a Fire Flower",
    "halfway": "Made it halfway through 1-1",
    "level": "Cleared a level",
    "first_death": "Lost a life (it happens)",
    "comeback": "Got back up after losing a life",
    "high_score": "Set a new high score",
    "long_run": "Longest run without dying",
}

HALFWAY_1_1 = 1600  # pixels; World 1-1 is roughly 3,200 pixels long


class Tracker:
    def __init__(self, data_dir: str):
        self.path = os.path.join(data_dir, "stats.json")
        self.stats = {
            "unlocked": [],
            "high_score": 0,
            "deaths": 0,
            "levels_cleared": 0,
            "decisions": 0,
            "longest_run": 0,
            "current_run": 0,
            "best_x": {},
            "attempts": {},
            "completions": {},
        }
        if os.path.exists(self.path):
            try:
                with open(self.path, encoding="utf-8") as f:
                    self.stats.update(json.load(f))
            except (OSError, ValueError):
                pass
        self._died_last_step = False

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2)

    def _unlock(self, key: str, events: List[str]) -> None:
        if key not in self.stats["unlocked"]:
            self.stats["unlocked"].append(key)
            events.append("Achievement: " + ACHIEVEMENTS[key])

    def start(self, state: GameState) -> None:
        self.stats["attempts"][state.stage] = self.stats["attempts"].get(state.stage, 0) + 1

    def update(self, before: GameState, after: GameState) -> List[str]:
        """Record one move. Returns the events to show on the dashboard."""
        s = self.stats
        events: List[str] = []
        s["decisions"] += 1
        stage = after.stage
        s["best_x"][stage] = max(s["best_x"].get(stage, 0), after.x)

        if self._died_last_step and after.lives == before.lives:
            self._unlock("comeback", events)
        self._died_last_step = False

        if after.powerup > before.powerup:
            if after.powerup == 1:
                self._unlock("mushroom", events)
                events.append("Mario grew bigger.")
            elif after.powerup >= 2:
                self._unlock("fire", events)
                events.append("Mario got fire power.")

        if stage == "1-1" and before.x < HALFWAY_1_1 <= after.x:
            self._unlock("halfway", events)

        if (after.world, after.level) > (before.world, before.level):
            s["levels_cleared"] += 1
            s["completions"][before.stage] = s["completions"].get(before.stage, 0) + 1
            s["attempts"][stage] = s["attempts"].get(stage, 0) + 1
            self._unlock("level", events)
            events.append("Cleared %s." % before.stage)

        if after.lives < before.lives:
            s["deaths"] += 1
            self._died_last_step = True
            s["attempts"][stage] = s["attempts"].get(stage, 0) + 1
            self._unlock("first_death", events)
            events.append("Lost a life on %s at %d px." % (before.stage, before.x))
            if s["current_run"] > s["longest_run"]:
                s["longest_run"] = s["current_run"]
                if s["deaths"] > 1:
                    self._unlock("long_run", events)
            s["current_run"] = 0
        else:
            s["current_run"] += 1

        if after.score > s["high_score"]:
            if s["high_score"] > 0 and before.score <= s["high_score"]:
                self._unlock("high_score", events)
            s["high_score"] = after.score

        self.save()
        return events

    @staticmethod
    def outcome(before: GameState, after: GameState) -> str:
        """One short phrase for memory: what this move led to."""
        if after.lives < before.lives:
            return "Mario lost a life"
        if (after.world, after.level) > (before.world, before.level):
            return "the level was cleared"
        if after.powerup > before.powerup:
            return "Mario powered up"
        if after.powerup < before.powerup:
            return "Mario got hurt"
        moved = after.x - before.x
        gained = after.score - before.score
        text = "moved %+d px" % moved
        if gained > 0:
            text += " and scored %d" % gained
        return text

    def unlocked_labels(self) -> List[dict]:
        return [{"key": k, "label": ACHIEVEMENTS[k]} for k in self.stats["unlocked"] if k in ACHIEVEMENTS]

    def summary(self, state: Optional[GameState] = None) -> dict:
        s = self.stats
        return {
            "high_score": s["high_score"],
            "deaths": s["deaths"],
            "levels_cleared": s["levels_cleared"],
            "decisions": s["decisions"],
            "longest_run": max(s["longest_run"], s["current_run"]),
            "best_x": s["best_x"],
            "attempts": s["attempts"],
            "completions": s["completions"],
            "achievements": self.unlocked_labels(),
            "achievements_total": len(ACHIEVEMENTS),
        }
