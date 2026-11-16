from fakes import FakeGame

from mario_ai import game_state as gs


def test_reads_position_score_and_status():
    game = FakeGame()
    game.set_x(3 * 256 + 20)
    game.set_score(12340)
    game.ram[gs.POWERUP] = 1
    game.ram[gs.WORLD] = 0
    game.ram[gs.LEVEL] = 1
    state = gs.read_state(game.read_memory)
    assert state.x == 788
    assert state.score == 12340
    assert state.stage == "1-2"
    assert state.powerup_name == "big"
    assert state.time_left == 400
    assert state.lives == 2


def test_bcd_digits():
    assert gs.bcd_digits(bytes([0, 1, 2, 3, 4, 5])) == 12345


def test_enemies_are_relative_to_mario_and_described():
    game = FakeGame()
    game.set_x(100)
    game.enemy(0, 110)
    game.enemy(2, 160)
    state = gs.read_state(game.read_memory)
    assert state.enemies_ahead == [10, 60]
    text = state.describe()
    assert "right in front of Mario (10 px)" in text
    assert "ahead (60 px)" in text


def test_no_enemies():
    state = gs.read_state(FakeGame().read_memory)
    assert "No enemies nearby." in state.describe()
