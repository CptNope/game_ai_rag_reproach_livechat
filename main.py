from flask_socketio import SocketIO, emit

import time
import os
import json
from retroarch_interface.screenshot import capture_screen
from embedding_engine.embed import embed_text
from reproach_index.query import query
from ollama_agent.generate_action import generate_action
from utils.describe_state import describe_state
from utils.state_hash import hash_state
import pyautogui

# Log folder
os.makedirs("game_memory/logs", exist_ok=True)
chat_log_path = "game_memory/logs/chat_log.txt"

last_hash = None
frame_count = 0

def send_action(action):
    if "jump" in action:
        pyautogui.press('space')
    elif "left" in action:
        pyautogui.keyDown('left')
        time.sleep(0.2)
        pyautogui.keyUp('left')
    elif "right" in action:
        pyautogui.keyDown('right')
        time.sleep(0.2)
        pyautogui.keyUp('right')

def log_to_terminal_and_file(message):
    print(message)
    with open(chat_log_path, "a") as f:
        f.write(message + "\n")

def game_loop(poll_every=10):
    global last_hash, frame_count
    print("Starting MegaMan AI Game Loop...")
    log_to_terminal_and_file("=== MegaMan AI Game Log ===")

    while True:
        frame_count += 1
        if frame_count % poll_every != 0:
            time.sleep(0.016)
            continue

        # 1. Capture screen
        img = capture_screen()
        img_path = f"game_memory/logs/frame_{frame_count}.png"
        img.save(img_path)

        # 2. Get game state
        description = describe_state()
        game_state = {
            "frame": frame_count,
            "description": description
        }

        # 3. Skip duplicates
        current_hash = hash_state(game_state)
        if current_hash == last_hash:
            continue
        last_hash = current_hash

        # 4. Embed + retrieve
        vec = embed_text(description)
        docs = query(description, top_k=3)
        context = "\n".join([d["text"] for d in docs])

        # 5. Generate prompt
        prompt = f"""Game Situation: {description}
Previous Knowledge:
{context}
What should the player do next?
"""

        # 6. AI decision
        action = generate_action(prompt)

        # 7. Show readable output
        log_to_terminal_and_file(f"[Frame {frame_count}]")
        log_to_terminal_and_file(f"AI observes: {description}")
        log_to_terminal_and_file(f"Retrieved memory: {context}")
        log_to_terminal_and_file(f"AI decides: {action}")
        log_to_terminal_and_file("-" * 40)

        # 8. Send to game
        send_action(action)

        # 9. Save log
        with open(f"game_memory/logs/step_{frame_count}.json", "w") as f:
            json.dump({"state": game_state, "action": action}, f, indent=2)


        
        # === ACHIEVEMENT CHECK ===
        achievement_path = "game_memory/logs/achievements.json"
        if not os.path.exists(achievement_path):
            with open(achievement_path, "w") as af:
                json.dump([], af)

        with open(achievement_path, "r") as af:
            unlocked = json.load(af)

        # Check for basic Mario achievements
        checks = {
            "🥇 Got Fire Flower": reward_state.get("powerup_state") == 2,
            "🍄 Got Mushroom": reward_state.get("powerup_state") == 1,
            "🧱 Reached Half-Level": reward_state.get("player_x", 0) > 120,
            "🏁 Reached End of Level": reward_state.get("player_x", 0) > 220,
        }

        
        for label, condition in checks.items():
            if condition and label not in unlocked:
                unlocked.append(label)
                print(f"[ACHIEVEMENT UNLOCKED] {label}")
                with open("game_memory/logs/chat_log.txt", "a") as chat:
                    chat.write(f"[ACHIEVEMENT] {label}\n")
                try:
                    from reward_dashboard_live import socketio
                    socketio.emit("toast", label)
                except Exception as e:
                    pass

            if condition and label not in unlocked:
                unlocked.append(label)
                print(f"[ACHIEVEMENT UNLOCKED] {label}")
                with open("game_memory/logs/chat_log.txt", "a") as chat:
                    chat.write(f"[ACHIEVEMENT] {label}\n")

        with open(achievement_path, "w") as af:
            json.dump(unlocked, af)
\n        
        # === ADVANCED STATS + ACHIEVEMENTS ===
        stat_path = "game_memory/logs/ai_stats.json"
        if not os.path.exists(stat_path):
            with open(stat_path, "w") as f:
                json.dump({"highest_score": 0, "longest_survival": 0, "deaths": 0, "retries": 0}, f)

        with open(stat_path, "r") as f:
            stats = json.load(f)

        current_score = reward
        survival_time = frame_count
        died = reward_state.get("powerup_state") == 0 and reward_state.get("player_x", 0) < 5

        # Track personal bests
        new_stats = []
        if current_score > stats["highest_score"]:
            stats["highest_score"] = current_score
            new_stats.append("🏅 New High Score!")

        if survival_time > stats["longest_survival"]:
            stats["longest_survival"] = survival_time
            new_stats.append("🏃 Longest Survival Streak!")

        if died:
            stats["deaths"] += 1
            new_stats.append("☠️ Mario Died")
            if stats["deaths"] > stats["retries"]:
                stats["retries"] += 1
                new_stats.append("🔁 Try Again Unlocked!")

        # Emit any new stats
        for s in new_stats:
            try:
                from reward_dashboard_live import socketio
                socketio.emit("toast", s)
            except:
                pass
            with open("game_memory/logs/chat_log.txt", "a") as chat:
                chat.write(f"[STAT] {s}\n")

        with open(stat_path, "w") as f:
            json.dump(stats, f)

        
        # === LEVEL TRACKING ===
        level_path = "game_memory/logs/level_stats.json"
        if not os.path.exists(level_path):
            with open(level_path, "w") as f:
                json.dump({}, f)

        with open(level_path, "r") as f:
            level_data = json.load(f)

        # For demo: we assume 1-1 unless RAM/ROM map used
        current_level = "1-1"

        if current_level not in level_data:
            level_data[current_level] = {"attempts": 0, "completions": 0}

        level_data[current_level]["attempts"] += 1

        if reward_state.get("player_x", 0) > 220:
            level_data[current_level]["completions"] += 1
            try:
                from reward_dashboard_live import socketio
                socketio.emit("toast", f"🏁 Completed {current_level}")
            except:
                pass
            with open("game_memory/logs/chat_log.txt", "a") as chat:
                chat.write(f"[LEVEL COMPLETE] {current_level}\n")

        with open(level_path, "w") as f:
            json.dump(level_data, f)

        # 10. Log reward data
        from retroarch_interface.read_mario_ram import read_ram_state, calculate_score
        reward_state = read_ram_state()
        reward = calculate_score(reward_state)
        with open("game_memory/logs/reinforce_log.jsonl", "a") as rf:
            rf.write(json.dumps({
                "frame": frame_count,
                "state": game_state,
                "action": action,
                "reward": reward
            }) + "\n")
\n        
        # CONTROL CHECK
        control_path = "game_memory/control.json"
        try:
            with open(control_path, "r") as cf:
                control = json.load(cf)

            # Pause loop
            if control.get("paused", False):
                print("[PAUSED] Waiting...")
                time.sleep(1)
                continue

            # Reset game
            if control.get("reset_game", False):
                os.system("python3 retroarch_interface/launch_with_state.py &")
                print("[RESET] Relaunched RetroArch from savestate.")
                control["reset_game"] = False

            # Log episode
            if control.get("log_episode", False):
                with open("game_memory/logs/episode_marks.txt", "a") as epf:
                    epf.write(f"EPISODE_MARK: frame {frame_count}\n")
                print(f"[LOG] Episode marked at frame {frame_count}")
                control["log_episode"] = False

            with open(control_path, "w") as cf:
                json.dump(control, cf)

        except Exception as e:
            print("Control file read error:", e)
\n        time.sleep(0.1)

if __name__ == "__main__":
    game_loop()
