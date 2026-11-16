"""Super Mario Bros. (NES) game state from system RAM.

Addresses come from the Data Crystal RAM map:
https://datacrystal.tcrf.net/wiki/Super_Mario_Bros./RAM_map
"""

from dataclasses import dataclass, field
from typing import Callable, List

# address: meaning
PLAYER_STATE = 0x000E
ENEMY_DRAWN = 0x000F  # 5 bytes, one per enemy slot
PLAYER_PAGE = 0x006D  # which 256-pixel page of the level Mario is on
PLAYER_SCREEN_X = 0x0086
ENEMY_SCREEN_X = 0x0087  # 5 bytes
PLAYER_Y = 0x00CE
POWERUP = 0x0756  # 0 small, 1 big, 2+ fire
LIVES = 0x075A
WORLD = 0x075F
LEVEL = 0x0760
SCORE = 0x07DD  # 6 BCD digits
TIMER = 0x07F8  # 3 BCD digits

POWERUP_NAMES = {0: "small", 1: "big"}


@dataclass
class GameState:
    world: int
    level: int
    x: int  # position in the level, in pixels
    screen_x: int
    y: int
    powerup: int
    lives: int
    score: int
    time_left: int
    player_state: int
    enemies_ahead: List[int] = field(default_factory=list)  # pixels to each visible enemy, positive = ahead

    @property
    def stage(self) -> str:
        return "%d-%d" % (self.world, self.level)

    @property
    def powerup_name(self) -> str:
        return POWERUP_NAMES.get(self.powerup, "fire")

    def describe(self) -> str:
        """A short plain-English summary the language model can reason about."""
        parts = [
            "World %s, %d pixels into the level." % (self.stage, self.x),
            {"small": "Mario is small.", "big": "Mario is big."}.get(self.powerup_name, "Mario has fire power."),
        ]
        close = sorted(d for d in self.enemies_ahead if -32 <= d <= 96)
        if not close:
            parts.append("No enemies nearby.")
        else:
            for d in close[:2]:
                if d < 0:
                    parts.append("An enemy is just behind Mario.")
                elif d < 24:
                    parts.append("An enemy is right in front of Mario (%d px)." % d)
                else:
                    parts.append("An enemy is ahead (%d px)." % d)
        if self.y > 200:
            parts.append("Mario is falling low on the screen.")
        parts.append("%d seconds left, %d %s." % (self.time_left, self.lives, "life" if self.lives == 1 else "lives"))
        return " ".join(parts)

    def to_dict(self) -> dict:
        return {
            "stage": self.stage, "x": self.x, "y": self.y, "powerup": self.powerup_name,
            "lives": self.lives, "score": self.score, "time_left": self.time_left,
            "enemies_ahead": self.enemies_ahead,
        }


def bcd_digits(values: bytes) -> int:
    """Score and timer store one decimal digit per byte."""
    total = 0
    for v in values:
        total = total * 10 + (v & 0x0F)
    return total


def read_state(read: Callable[[int, int], bytes]) -> GameState:
    """Build a GameState with a handful of memory reads (read(address, length) -> bytes)."""
    low = read(PLAYER_STATE, 0x00CF - PLAYER_STATE)  # 0x000E..0x00CE in one request

    def at(addr: int) -> int:
        return low[addr - PLAYER_STATE]

    status = read(POWERUP, LEVEL - POWERUP + 1)  # 0x0756..0x0760
    score = bcd_digits(read(SCORE, 6)) * 10  # the last digit on screen is always 0
    timer = bcd_digits(read(TIMER, 3))

    screen_x = at(PLAYER_SCREEN_X)
    x = at(PLAYER_PAGE) * 256 + screen_x
    enemies = [
        at(ENEMY_SCREEN_X + i) - screen_x
        for i in range(5)
        if at(ENEMY_DRAWN + i)
    ]
    return GameState(
        world=status[WORLD - POWERUP] + 1,
        level=status[LEVEL - POWERUP] + 1,
        x=x,
        screen_x=screen_x,
        y=at(PLAYER_Y),
        powerup=status[0],
        lives=status[LIVES - POWERUP],
        score=score,
        time_left=timer,
        player_state=at(PLAYER_STATE),
        enemies_ahead=enemies,
    )
