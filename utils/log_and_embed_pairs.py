
import os
import time
import json
import subprocess
from datetime import datetime
from retroarch_interface.read_megaman_ram import read_ram_state
from retroarch_interface.screenshot import capture_screen
from embedding_engine.embed import embed_text
from reproach import Document

# Paths
LOG_PATH = "game_memory/paired_logs"
EMBED_PATH = "reproach_index/docs"
REINDEX_SCRIPT = "reproach_index/reindex.py"
os.makedirs(LOG_PATH, exist_ok=True)
os.makedirs(EMBED_PATH, exist_ok=True)

REINDEX_EVERY = 10

def log_and_embed_pair(frame_id):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ram_state = read_ram_state()
    image_file = os.path.join(LOG_PATH, f"{frame_id}_{timestamp}.png")
    json_file = os.path.join(LOG_PATH, f"{frame_id}_{timestamp}.json")

    # Capture screen
    img = capture_screen()
    img.save(image_file)

    # Save RAM dump
    with open(json_file, "w") as f:
        json.dump(ram_state, f, indent=2)

    # Compose description for embedding
    desc = []
    if ram_state:
        if ram_state.get("health", 0) < 5:
            desc.append("Player has low health.")
        if ram_state.get("player_x", 0) < 50:
            desc.append("Player is on the left side.")
        if abs(ram_state.get("enemy_x", 0) - ram_state.get("player_x", 0)) < 20:
            desc.append("Enemy is very close.")
    text_summary = " ".join(desc) if desc else "Generic game state."

    # Save embedded doc
    doc = Document(id=f"{frame_id}_{timestamp}", text=text_summary)
    doc_path = os.path.join(EMBED_PATH, f"{doc.id}.json")
    with open(doc_path, "w") as f:
        json.dump({"id": doc.id, "text": doc.text}, f)

    print(f"Logged + embedded: {doc.id}")

def run_logger(interval_seconds=10, total_steps=50):
    for i in range(total_steps):
        log_and_embed_pair(i)

        # Trigger reindex every REINDEX_EVERY documents in background
        if i % REINDEX_EVERY == 0 and i != 0:
            print("Reindexing in background...")
            subprocess.Popen(["python3", REINDEX_SCRIPT])

        time.sleep(interval_seconds)

if __name__ == "__main__":
    run_logger()
