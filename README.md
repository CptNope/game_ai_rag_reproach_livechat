
# 🎮 Mario AI Companion — Full Real-Time Dashboard Edition

This project combines AI gameplay, real-time monitoring, and interactive control for **Super Mario Bros (NES)** using a custom AI agent.

---

## 🚀 Features

- ✅ AI-controlled Mario using RAM + LLM (DeepSeek, Ollama, or Transformers)
- 🔁 Reward logging + live visualization (Plotly)
- 🎥 Live game frame stream
- 🧠 Real-time AI state + console log in-browser
- 🛠️ Interactive Dashboard:
  - ⏸️ Pause / Resume AI
  - 🔄 Reset Game from Savestate
  - 📝 Manual Episode Logging
  - 💾 Save / Load State (slot 0)
  - 📦 One-click Export (logs + screenshots)

---

## 🧰 Requirements

- Linux / WSL (Ubuntu recommended)
- Python 3.9–3.11
- Optional: GPU + Ollama (or HuggingFace models)

Install dependencies:
```bash
pip install flask flask-socketio pillow matplotlib plotly
```

---

## 💡 How to Run

### 1. Start the Flask Dashboard
```bash
python utils/reward_dashboard_live.py
```

Then open:
```
http://localhost:5000
```

### 2. Start the AI loop
In another terminal:
```bash
python main.py
```

Mario will play with commentary and log reward over time.

---

## 📤 Exporting Sessions

Click the 📦 **Export Full Session** button to download:
- `chat_log.txt`
- `reinforce_log.jsonl`
- All `frame_*.png` screenshots

These are packaged into a ZIP file (`session_export.zip`).

---

## 💾 Savestate Slots

Use the dashboard buttons to:
- 💾 Save current state to **slot 0**
- 📥 Load previously saved state from **slot 0**

Extendable to multiple slots later.

---

## 📜 Logs + Rewards

Live data streamed from:
- `game_memory/logs/chat_log.txt`
- `game_memory/logs/reinforce_log.jsonl`

Plotted in-browser using Plotly.js and shown frame-by-frame.

---

## 🧠 Future Ideas

- Multi-slot support for savestates
- Auto-episode summarization + export
- MJPEG or RTSP video feed
- RL fine-tuning from collected sessions

---

Made by SciStories & ChatGPT. Ready for AI-assisted retro research labs 🍄🧠
