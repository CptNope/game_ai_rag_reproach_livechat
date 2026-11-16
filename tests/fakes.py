"""A tiny fake of Super Mario Bros. RAM, RetroArch and a keyboard, for tests and demos."""

from mario_ai import game_state as gs


class FakeGame:
    """Holds 2 KB of NES RAM and moves Mario when buttons are pressed."""

    def __init__(self):
        self.ram = bytearray(0x800)
        self.ram[gs.LIVES] = 2
        self.ram[gs.PLAYER_Y] = 176
        self.set_x(40)
        self.set_timer(400)
        self.paused = False
        self.commands = []

    def set_x(self, x):
        self.ram[gs.PLAYER_PAGE] = x // 256
        self.ram[gs.PLAYER_SCREEN_X] = x % 256

    def x(self):
        return self.ram[gs.PLAYER_PAGE] * 256 + self.ram[gs.PLAYER_SCREEN_X]

    def set_score(self, points):
        digits = str(points // 10).rjust(6, "0")[-6:]
        for i, d in enumerate(digits):
            self.ram[gs.SCORE + i] = int(d)

    def set_timer(self, seconds):
        for i, d in enumerate(str(seconds).rjust(3, "0")):
            self.ram[gs.TIMER + i] = int(d)

    def enemy(self, slot, screen_x):
        self.ram[gs.ENEMY_DRAWN + slot] = 1
        self.ram[gs.ENEMY_SCREEN_X + slot] = screen_x % 256

    # RetroArch interface
    def read_memory(self, address, length):
        return bytes(self.ram[address:address + length])

    def status(self):
        return "PAUSED" if self.paused else "PLAYING"

    def command(self, name):
        self.commands.append(name)
        if name == "PAUSE_TOGGLE":
            self.paused = not self.paused

    # Keyboard interface (KeyboardController backend)
    def keyDown(self, key):
        if key == "right":
            self.set_x(self.x() + 24)
        elif key == "x":
            self.set_score(self.score() + 100)

    def keyUp(self, key):
        pass

    def score(self):
        return gs.bcd_digits(self.read_memory(gs.SCORE, 6)) * 10
