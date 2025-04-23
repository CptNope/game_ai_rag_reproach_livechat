
import struct
import json

# Path to your .srm file (edit as needed)
SRM_PATH = "demo_game_assets/megaman.srm"

# RAM offsets based on Mega Man NES RAM map
RAM_OFFSETS = {
    "player_x": 0x0003,
    "player_y": 0x0004,
    "health": 0x0014,
    "weapon_energy": 0x0020,
    "enemy_x": 0x0040,
    "enemy_y": 0x0041,
}

def read_ram_state(srm_path=SRM_PATH):
    state = {}
    try:
        with open(srm_path, "rb") as f:
            for name, offset in RAM_OFFSETS.items():
                f.seek(offset)
                value = struct.unpack("B", f.read(1))[0]  # Unsigned 8-bit
                state[name] = value
    except FileNotFoundError:
        print(f"File not found: {srm_path}")
    return state

if __name__ == "__main__":
    state = read_ram_state()
    print(json.dumps(state, indent=2))
