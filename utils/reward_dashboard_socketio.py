
from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import os
import json
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mariobot'
socketio = SocketIO(app, cors_allowed_origins="*")

LOG_PATH = "game_memory/logs/reinforce_log.jsonl"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mario AI Live Dashboard</title>
    <script src="https://cdn.socket.io/4.4.1/socket.io.min.js"></script>
    <script>
        document.addEventListener("DOMContentLoaded", () => {
            const socket = io();
            socket.on("ai_update", data => {
                document.getElementById("state").innerText = data.description;
                document.getElementById("reward").innerText = "Reward: " + data.reward;
                document.getElementById("frame").innerText = "Frame: " + data.frame;
            });
        });
    </script>
</head>
<body style="font-family: sans-serif; padding: 20px;">
    <h1>🎮 Mario AI Live Dashboard</h1>
    <p id="frame">Frame: --</p>
    <p id="state">Waiting for state...</p>
    <p id="reward">Reward: --</p>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

def tail_log():
    seen = set()
    while True:
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r") as f:
                lines = f.readlines()[-5:]
                for line in lines:
                    try:
                        obj = json.loads(line)
                        if obj["frame"] not in seen:
                            emit_data = {
                                "frame": obj["frame"],
                                "reward": obj.get("reward", 0),
                                "description": obj["state"].get("description", "unknown")
                            }
                            socketio.emit("ai_update", emit_data)
                            seen.add(obj["frame"])
                    except:
                        continue
        time.sleep(2)

@socketio.on("connect")
def handle_connect():
    print("Client connected")

if __name__ == "__main__":
    thread = threading.Thread(target=tail_log)
    thread.daemon = True
    thread.start()
    socketio.run(app, host="0.0.0.0", port=5000)
