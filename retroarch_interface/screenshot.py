
import mss
import numpy as np
from PIL import Image

def capture_screen(region=None):
    with mss.mss() as sct:
        monitor = region if region else sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        return img

if __name__ == "__main__":
    img = capture_screen()
    img.save("screenshot.png")
