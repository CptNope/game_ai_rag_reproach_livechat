
import subprocess
import os

# Edit these as needed
RETROARCH_PATH = "/usr/bin/retroarch"  # Path to RetroArch binary
CORE_PATH = "/path/to/cores/nestopia_libretro.so"
ROM_PATH = "/path/to/roms/MegaMan.nes"
STATE_SLOT = 0  # Change if using different slot

def launch_with_state():
    # Construct the command
    command = [
        RETROARCH_PATH,
        "-L", CORE_PATH,
        ROM_PATH,
        "--state-slot", str(STATE_SLOT),
        "--load-state"
    ]
    subprocess.Popen(command)

if __name__ == "__main__":
    launch_with_state()
