
# 🧠 Mario AI Companion — Full Dashboard + Stats Edition

This system builds a real-time AI assistant that plays Super Mario Bros (NES), learns from memory, and displays all decisions, metrics, and milestones in a visual dashboard.

---

## 🚀 Features

- ✅ AI plays Mario using RAM analysis, RAG, and LLM reasoning
- 🎮 Live game frame stream + RAM-to-language state display
- 📈 Reward and score plotting in real time (Plotly.js)
- 🛠️ Browser-based Dashboard with full control:
  - ⏸️ Pause / Resume AI loop
  - 🔄 Reset game from savestate
  - 💾 Save / 📥 Load slot 0
  - 📝 Log episode manually
  - 📦 Export session logs + screenshots
- 🏆 Achievement system with toast popups
- 📊 AI stats and graphs (survival, retries, scores, levels)
- 📍 Level-based tracking (attempts + completions)
- 🧾 Chat log + event console viewer
- 🔄 Live syncing via Flask-SocketIO

---

## 📂 Folder Structure

- `game_memory/logs/` — stores screenshots, logs, achievements, and stats
- `utils/reward_dashboard_live.py` — Flask + WebSocket server
- `main.py` — AI game loop
- `retroarch_interface/` — emulator RAM parsing scripts

---

## 📦 Install Requirements

```bash
pip install flask flask-socketio matplotlib pillow plotly
```

Optional for AI:
```bash
pip install axolotl transformers sentence-transformers peft bitsandbytes
```

---

## 🧑‍💻 How to Use

### 1. Run the Flask Dashboard
```bash
python utils/reward_dashboard_live.py
```
Then open:
```
http://localhost:5000
```

### 2. Start the AI Player
```bash
python main.py
```

---

## 📤 Export Everything

Click **Export Session** to download:
- Screenshots: `frame_*.png`
- Logs: `chat_log.txt`, `reinforce_log.jsonl`
- Stats: `ai_stats.json`, `level_stats.json`, `achievements.json`

---

## 🏆 Achievements

- 🍄 Got Mushroom
- 🥇 Got Fire Flower
- 🧱 Reached Half Level
- 🏁 Finished Level
- ☠️ Died
- 🔁 Retry after Death
- 🏅 New High Score
- 🏃 Longest Survival

Shown as:
- 📜 Console messages
- 🎉 Popup toast notifications
- 🏆 Dashboard achievement list

---

## 📈 AI Stats Visualized

- Bar charts for:
  - Level Attempts
  - Level Completions
- Coming soon:
  - Death vs Retry counts
  - Score per session
  - Timeline survival plots

---

## 🧠 Model Support

Works with:
- Ollama (`deepseek-coder`)
- Transformers via Axolotl (LoRA fine-tuning ready)
- JSONL export for training custom models

---

## 🧪 Future Roadmap

- Multi-agent scoreboard view
- RetroAchievement API sync
- Training graphs + timeline export
- MJPEG video stream for Pi/Web

---

Built for retro AI research, gamified training, and fun 👾🍄
