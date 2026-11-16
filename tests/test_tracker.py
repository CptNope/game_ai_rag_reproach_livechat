from fakes import FakeGame

from mario_ai import game_state as gs
from mario_ai.tracker import Tracker


def states(mutate):
    game = FakeGame()
    before = gs.read_state(game.read_memory)
    mutate(game)
    return before, gs.read_state(game.read_memory)


def test_mushroom_and_fire(tmp_path):
    t = Tracker(str(tmp_path))
    before, after = states(lambda g: g.ram.__setitem__(gs.POWERUP, 1))
    events = t.update(before, after)
    assert "Achievement: Got a Super Mushroom" in events
    assert Tracker.outcome(before, after) == "Mario powered up"


def test_death_then_comeback(tmp_path):
    t = Tracker(str(tmp_path))
    before, after = states(lambda g: g.ram.__setitem__(gs.LIVES, 1))
    events = t.update(before, after)
    assert t.stats["deaths"] == 1
    assert "Achievement: Lost a life (it happens)" in events
    assert Tracker.outcome(before, after) == "Mario lost a life"
    b2, a2 = states(lambda g: None)
    assert "Achievement: Got back up after losing a life" in t.update(b2, a2)


def test_level_clear_counts_completion(tmp_path):
    t = Tracker(str(tmp_path))
    before, after = states(lambda g: g.ram.__setitem__(gs.LEVEL, 1))
    events = t.update(before, after)
    assert "Cleared 1-1." in events
    assert t.stats["completions"]["1-1"] == 1
    assert t.stats["levels_cleared"] == 1


def test_high_score_only_after_a_first_score(tmp_path):
    t = Tracker(str(tmp_path))
    before, after = states(lambda g: g.set_score(500))
    assert not any("high score" in e for e in t.update(before, after))
    b2, a2 = states(lambda g: g.set_score(900))
    assert "Achievement: Set a new high score" in t.update(b2, a2)


def test_stats_persist(tmp_path):
    t = Tracker(str(tmp_path))
    before, after = states(lambda g: g.set_x(200))
    t.update(before, after)
    assert Tracker(str(tmp_path)).stats["best_x"]["1-1"] == 200
