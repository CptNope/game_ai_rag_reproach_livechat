
import os
import json

LOG_PATH = "game_memory/logs"
OUTPUT_PATH = "fine_tuning_data"
os.makedirs(OUTPUT_PATH, exist_ok=True)

def extract_instruction_from_state(state):
    parts = []

    if state.get("player_x", 0) < 50:
        parts.append("Player is on the left.")
    elif state.get("player_x", 0) > 200:
        parts.append("Player is on the right.")
    else:
        parts.append("Player is near the center.")

    health = state.get("health", 0)
    if health > 10:
        parts.append("Player has high health.")
    elif health > 5:
        parts.append("Player has moderate health.")
    else:
        parts.append("Player has low health.")

    distance = abs(state.get("enemy_x", 0) - state.get("player_x", 0))
    if distance < 20:
        parts.append("Enemy is very close.")
    elif distance < 50:
        parts.append("Enemy is nearby.")
    else:
        parts.append("Enemy is far away.")

    weapon = state.get("weapon_energy", 0)
    if weapon < 5:
        parts.append("Weapon energy is low.")
    else:
        parts.append("Weapon energy is sufficient.")

    return "Game state: " + " ".join(parts)

def build_fine_tune_dataset():
    output_file = os.path.join(OUTPUT_PATH, "megaman_finetune_data.jsonl")
    entries = []

    for file in os.listdir(LOG_PATH):
        if file.endswith(".json"):
            path = os.path.join(LOG_PATH, file)
            with open(path, "r") as f:
                data = json.load(f)
                state = data.get("state", {})
                action = data.get("action", "").strip()
                if state and action:
                    entry = {
                        "instruction": extract_instruction_from_state(state),
                        "input": "",
                        "output": action
                    }
                    entries.append(entry)

    with open(output_file, "w") as out:
        for entry in entries:
            out.write(json.dumps(entry) + "\n")

    print(f"Wrote {len(entries)} fine-tuning samples to {output_file}")

if __name__ == "__main__":
    build_fine_tune_dataset()
