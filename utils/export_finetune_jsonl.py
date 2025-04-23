
import os
import json

LOG_PATH = "game_memory/logs"
OUTPUT_PATH = "game_memory/megaman_finetune.jsonl"

def load_logs():
    examples = []
    for file in os.listdir(LOG_PATH):
        if file.endswith(".json") and "step_" in file:
            with open(os.path.join(LOG_PATH, file), "r") as f:
                try:
                    data = json.load(f)
                    description = data["state"].get("description", "").strip()
                    action = data.get("action", "").strip()

                    if description and action:
                        examples.append({
                            "instruction": f"Game state: {description} What should the player do?",
                            "input": "",
                            "output": action
                        })
                except Exception as e:
                    print(f"Error reading {file}: {e}")
    return examples

def export_jsonl(examples):
    with open(OUTPUT_PATH, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")
    print(f"Exported {len(examples)} fine-tuning samples to {OUTPUT_PATH}")

if __name__ == "__main__":
    data = load_logs()
    export_jsonl(data)
