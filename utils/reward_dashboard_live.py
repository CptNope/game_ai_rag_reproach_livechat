
from flask import Flask, render_template_string, send_file, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import os
import json
import threading
import time
import zipfile
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mariobot'
socketio = SocketIO(app, cors_allowed_origins="*")

LOG_PATH = "game_memory/logs/reinforce_log.jsonl"
CHAT_LOG_PATH = "game_memory/logs/chat_log.txt"
FRAME_PATH = "game_memory/logs/frame_latest.png"
CONTROL_PATH = "game_memory/control.json"
EXPORT_PATH = "game_memory/exports"

# Ensure export directory exists
os.makedirs(EXPORT_PATH, exist_ok=True)

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Mario AI Dashboard</title>
  <script src="https://cdn.socket.io/4.4.1/socket.io.min.js"></script>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
  <style>
    body { font-family: sans-serif; background: #f2f2f2; padding: 20px; }
    .panel { background: #fff; padding: 1em; margin-bottom: 20px; border-radius: 10px; }
    button { padding: 10px; margin: 5px; font-size: 16px; }
    #frameimg { width: 400px; border: 1px solid #ccc; }
    #chatlog { height: 200px; overflow-y: scroll; background: #111; color: #0f0; font-family: monospace; padding: 10px; border-radius: 5px; }
  </style>
</head>
<body>
  <h1>🧠 Mario AI Live Dashboard</h1>

  <div class="panel">
    <h2>🎮 Game Frame</h2>
    <img id="frameimg" src="/frame?t=" + new Date().getTime()>
  </div>

  <div class="panel">
    <h2>📈 Reward Chart</h2>
    <div id="rewardchart" style="height:300px;"></div>
  </div>

  <div class="panel">
    <h2>AI State</h2>
    <p id="frame">Frame: --</p>
    <p id="state">--</p>
    <p id="reward">Reward: --</p>
  </div>

  <div class="panel">
    <h2>📜 Console Log</h2>
    <div id="chatlog">Waiting for logs...</div>
  </div>

  <div class="panel">
    <h2>🛠️ AI Controls</h2>
    <button onclick="sendControl('pause')">⏸️ Pause / Resume AI</button>
    <button onclick="sendControl('reset')">🔄 Reset Game</button>
    <button onclick="sendControl('log')">📝 Log Episode</button>
    <button onclick="sendSlot('save')">💾 Save State (Slot 0)</button>
    <button onclick="sendSlot('load')">📥 Load State (Slot 0)</button>
    <a href="/export" target="_blank"><button>📦 Export Full Session ZIP</button></a>
  </div>

  <script>
    const socket = io();
    let rewardData = [], frameLabels = [];

    socket.on("ai_update", data => {
      document.getElementById("frame").innerText = "Frame: " + data.frame;
      document.getElementById("state").innerText = data.description;
      document.getElementById("reward").innerText = "Reward: " + data.reward;
      rewardData.push(data.reward);
      frameLabels.push(data.frame);
      Plotly.react("rewardchart", [{
        x: frameLabels,
        y: rewardData,
        type: 'scatter',
        mode: 'lines+markers',
        line: { color: 'blue' }
      }], { margin: { t: 10 } });
      document.getElementById("frameimg").src = "/frame?t=" + new Date().getTime();
    });

    socket.on("chat_update", log => {
      const div = document.getElementById("chatlog");
      div.textContent = log;
      div.scrollTop = div.scrollHeight;
    });

    function sendControl(action) {
      fetch('/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      }).then(r => r.json()).then(console.log);
    }

    function sendSlot(slot_action) {
      fetch('/slot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slot: 0, action: slot_action })
      }).then(r => r.json()).then(console.log);
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(open("utils/templates/dashboard_toast.html").read())

@app.route("/frame")
def frame():
    if os.path.exists(FRAME_PATH):
        return send_file(FRAME_PATH, mimetype="image/png")
    return "Frame not found.", 404

@app.route("/control", methods=["POST"])
def control():
    action = request.json.get("action")
    if not action:
        return jsonify({"status": "error", "msg": "No action received"}), 400

    with open(CONTROL_PATH, "r") as f:
        state = json.load(f)

    if action == "pause":
        state["paused"] = not state["paused"]
    elif action == "reset":
        state["reset_game"] = True
    elif action == "log":
        state["log_episode"] = True

    with open(CONTROL_PATH, "w") as f:
        json.dump(state, f)

    return jsonify({"status": "ok", "control": state})

@app.route("/slot", methods=["POST"])
def slot_control():
    req = request.json
    action = req.get("action")
    slot = req.get("slot", 0)

    if action == "save":
        os.system(f"retroarch --screenshot --state-slot {slot} --save-state")
    elif action == "load":
        os.system(f"retroarch --state-slot {slot} --load-state")

    return jsonify({"status": "ok", "action": action, "slot": slot})

@app.route("/export")
def export_logs():
    zipname = os.path.join(EXPORT_PATH, "session_export.zip")
    with zipfile.ZipFile(zipname, 'w') as zf:
        for fname in ["chat_log.txt", "reinforce_log.jsonl"]:
            fpath = os.path.join("game_memory/logs", fname)
            if os.path.exists(fpath):
                zf.write(fpath, arcname=fname)
        # Include screenshots
        for fname in os.listdir("game_memory/logs"):
            if fname.startswith("frame_") and fname.endswith(".png"):
                zf.write(os.path.join("game_memory/logs", fname), arcname=f"screens/{fname}")
    return send_from_directory(EXPORT_PATH, "session_export.zip", as_attachment=True)

def tail_log():
    seen = set()
    chat_seen = 0
    while True:
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r") as f:
                lines = f.readlines()[-5:]
                for line in lines:
                    try:
                        obj = json.loads(line)
                        if obj["frame"] not in seen:
                            socketio.emit("ai_update", {
                                "frame": obj["frame"],
                                "reward": obj.get("reward", 0),
                                "description": obj["state"].get("description", "unknown")
                            })
                            seen.add(obj["frame"])
                    except:
                        continue

        if os.path.exists(CHAT_LOG_PATH):
            with open(CHAT_LOG_PATH, "r") as cf:
                lines = cf.readlines()
                if len(lines) != chat_seen:
                    socketio.emit("chat_update", "".join(lines[-30:]))
                    chat_seen = len(lines)

        time.sleep(2)

def copy_latest_frame():
    while True:
        log_dir = "game_memory/logs"
        latest = sorted([f for f in os.listdir(log_dir) if f.startswith("frame_") and f.endswith(".png")])
        if latest:
            src = os.path.join(log_dir, latest[-1])
            dst = os.path.join(log_dir, "frame_latest.png")
            try:
                Image.open(src).save(dst)
            except:
                pass
        time.sleep(2)

if __name__ == "__main__":
    threading.Thread(target=tail_log, daemon=True).start()
    threading.Thread(target=copy_latest_frame, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=5000)

@app.route("/achievements")
def get_achievements():
    path = "game_memory/logs/achievements.json"
    if not os.path.exists(path):
        return jsonify([])
    with open(path, "r") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/stats")
def get_stats():
    level_path = "game_memory/logs/level_stats.json"
    if not os.path.exists(level_path):
        return jsonify({"levels": {}})
    with open(level_path, "r") as f:
        levels = json.load(f)
    return jsonify({"levels": levels})
