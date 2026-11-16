"""Press buttons in RetroArch by sending keys to its window.

RetroArch's network commands can't press game buttons, so moves are sent
as key presses using RetroArch's default keyboard layout for player 1:
arrows to move, X for A (jump), Z for B (run). The RetroArch window
needs to be focused.
"""

import time

ACTIONS = {
    "right": ["right"],
    "run_right": ["right", "z"],
    "jump": ["x"],
    "jump_right": ["right", "x"],
    "run_jump_right": ["right", "z", "x"],
    "left": ["left"],
    "wait": [],
}


class KeyboardController:
    def __init__(self, backend=None):
        self._keys = backend

    def _backend(self):
        if self._keys is None:
            import pyautogui  # Imported here so tests and headless runs don't need a display.

            pyautogui.PAUSE = 0
            self._keys = pyautogui
        return self._keys

    def perform(self, action: str, hold: float) -> None:
        keys = ACTIONS.get(action, [])
        if not keys:
            time.sleep(hold)
            return
        backend = self._backend()
        for key in keys:
            backend.keyDown(key)
        try:
            time.sleep(hold)
        finally:
            for key in reversed(keys):
                backend.keyUp(key)
