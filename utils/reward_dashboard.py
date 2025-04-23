
from flask import Flask, render_template_string, send_file
import os
import json

app = Flask(__name__)
LOG_PATH = "game_memory/logs/reinforce_log.jsonl"
PLOT_PATH = "game_memory/logs/reward_episodes_plot.png"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Mario AI Reward Dashboard</title>
    <style>
        body { font-family: sans-serif; padding: 20px; background: #fafafa; }
        img { max-width: 100%; }
        .episode-summary { white-space: pre; background: #eee; padding: 1em; border-radius: 8px; }
    </style>
</head>
<body>
    <h1>🍄 Mario AI Reward Dashboard</h1>
    <p>This dashboard shows real-time learning metrics from AI gameplay.</p>
    <h2>Reward Plot</h2>
    <img src="/plot" alt="Reward Plot">
    <h2>Episode Summary</h2>
    <div class="episode-summary">{{ summary }}</div>
</body>
</html>
"""

def load_summary():
    if not os.path.exists(LOG_PATH):
        return "No log file found."

    episodes = []
    current = []
    last_frame = -100
    threshold = 50

    with open(LOG_PATH, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                frame = entry["frame"]
                reward = entry["reward"]

                if frame - last_frame > threshold and current:
                    episodes.append(current)
                    current = []

                current.append((frame, reward))
                last_frame = frame
            except:
                continue

    if current:
        episodes.append(current)

    summary = []
    for i, ep in enumerate(episodes):
        frames = [step[0] for step in ep]
        rewards = [step[1] for step in ep]
        if not frames or not rewards:
            continue
        survival = frames[-1] - frames[0]
        total = rewards[-1] - rewards[0]
        avg = total / max(1, len(rewards))
        summary.append(f"Episode {i+1}: Survived {survival} frames | Reward {total} | Avg/frame {avg:.2f}")

    return "\n".join(summary)

@app.route("/")
def dashboard():
    summary = load_summary()
    return render_template_string(HTML_TEMPLATE, summary=summary)

@app.route("/plot")
def plot():
    if not os.path.exists(PLOT_PATH):
        return "Plot not found.", 404
    return send_file(PLOT_PATH, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)
