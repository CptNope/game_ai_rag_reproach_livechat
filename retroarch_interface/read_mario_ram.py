
import struct
import json

# Path to your .srm file (edit as needed)
SRM_PATH = "demo_game_assets/mario.srm"

# RAM offsets for Super Mario Bros (NES)
RAM_OFFSETS = {
    "player_x": 0x0754,
    "player_y": 0x0756,
    "player_state": 0x075A,      # standing, jumping, etc.
    "powerup_state": 0x075E,     # 0 = small, 1 = mushroom, 2 = fire
    "enemy1_x": 0x07F8,
    "enemy1_y": 0x07FA,
    "score_1": 0x07DD,           # Score hundreds digit
    "score_2": 0x07DE,           # Score tens digit
    "score_3": 0x07DF,           # Score ones digit
}

def read_ram_state(srm_path=SRM_PATH):
    state = {}
    try:
        with open(srm_path, "rb") as f:
            for name, offset in RAM_OFFSETS.items():
                f.seek(offset)
                value = struct.unpack("B", f.read(1))[0]
                state[name] = value
    except FileNotFoundError:
        print(f"File not found: {srm_path}")
    return state

def calculate_score(state):
    return state.get("score_1", 0) * 100 + state.get("score_2", 0) * 10 + state.get("score_3", 0)

if __name__ == "__main__":
    state = read_ram_state()
    state["score_total"] = calculate_score(state)
    print(json.dumps(state, indent=2))
