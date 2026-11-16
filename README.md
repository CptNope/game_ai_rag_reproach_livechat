# Mario AI Companion

A local AI that plays Super Mario Bros. (NES) in RetroArch, remembers what worked, and shows every decision, stat and achievement on a live dashboard. Everything runs on your own computer with [Ollama](https://ollama.com).

Full write-up: [Building a Real-Time AI-Powered Mario Dashboard with Achievements and Stats](https://jeremyanderson.tech/building-a-real-time-ai-powered-mario-dashboard-with-achievements-stats/)

## How it works

1. **Reads the game.** Every move starts by reading Mario's position, power-up, lives, score, timer, world and nearby enemies straight from the console's memory, using RetroArch's network commands (`READ_CORE_MEMORY` over UDP).
2. **Describes it in words.** The numbers become a sentence a language model can reason about: "World 1-1, 280 pixels into the level. Mario is big. An enemy is right in front of Mario (20 px)."
3. **Remembers similar moments (RAG).** The situation is embedded with an Ollama embedding model and compared with past situations. The closest ones, with the move made and what happened next, go into the prompt.
4. **Decides.** A local model in Ollama picks a move, forced into valid JSON (`{"action": "jump_right", "reason": "..."}`) with Ollama's structured outputs.
5. **Plays and learns.** The move is pressed in RetroArch, the result ("moved +24 px and scored 50", "Mario lost a life") is saved to memory, and the dashboard updates.

By default RetroArch is paused while the model thinks, so even a slow model plays fairly.

## Dashboard

Open <http://localhost:5000> while it runs:

- What Mario sees right now, the move the AI chose and why, and the past moments it remembered
- Score, high score, lives, lives lost, levels cleared and longest run
- Charts of progress through the level and score
- Eight achievements, with pop-ups when one unlocks
- Attempts, clears and furthest point for each level
- An activity log
- Controls: pause and resume the AI, save and load a state, reset the game, mark an episode, and export the session

## What you need

- **RetroArch** with an NES core (for example FCEUmm, Nestopia or Mesen) and your own legally obtained copy of Super Mario Bros. No game files are included.
- **Network Commands turned on** in RetroArch: Settings > Network > Network Commands, port 55355 (or `network_cmd_enable = "true"` in `retroarch.cfg`).
- **RetroArch's default keyboard controls** for player 1: arrows to move, X for A (jump), Z for B (run). The RetroArch window must have focus while the AI plays.
- **Ollama** with a chat model and an embedding model:

  ```bash
  ollama pull llama3.2
  ollama pull nomic-embed-text
  ```

- **Python 3.10 or newer** on a computer with a screen (the AI presses keys with `pyautogui`).

## Run it

```bash
git clone https://github.com/CptNope/game_ai_rag_reproach_livechat
cd game_ai_rag_reproach_livechat
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Start RetroArch with the game, get Mario to the start of World 1-1, then:

```bash
python -m mario_ai
```

Open <http://localhost:5000>, then click back into the RetroArch window so it receives the key presses.

## Settings

| Variable | Default | What it does |
|---|---|---|
| `OLLAMA_MODEL` | `llama3.2` | Model that chooses moves |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Model that embeds situations for memory |
| `OLLAMA_URL` | `http://localhost:11434` | Where Ollama is running |
| `RETROARCH_HOST` / `RETROARCH_PORT` | `127.0.0.1` / `55355` | RetroArch network commands |
| `THINK_PAUSED` | `1` | Pause the game while the model thinks (`0` to play in real time) |
| `HOLD_TIME` | `0.35` | Seconds each move's keys are held |
| `STEP_DELAY` | `0.2` | Seconds between moves |
| `CAPTURE_FRAMES` | `0` | `1` shows screen captures on the dashboard (needs `pip install mss pillow`) |
| `DATA_DIR` | `game_memory` | Where memory, decisions and stats are saved |
| `HOST` / `PORT` | `127.0.0.1` / `5000` | Dashboard address |

The dashboard has no login, so keep it on `127.0.0.1` unless you put one in front of it.

## What gets saved

In `game_memory/`:

- `memory.jsonl`: every situation with its embedding, the move and what happened (the AI's long-term memory)
- `decisions.jsonl`: every decision with the model's reason, useful as training data for a fine-tuned model
- `stats.json`: stats, per-level progress and unlocked achievements

**Export session** on the dashboard downloads all three as a ZIP.

## Honest expectations

A general-purpose language model choosing one move at a time is not a strong Mario player. It reacts to a short description, not to the screen, and it only knows what the memory addresses tell it, so it can't see gaps or pipes. That's the point of the project: to watch how a model reasons, how memory changes its choices over time, and where it fails. Ideas to make it better are below.

## If something doesn't work

- **"No reply from RetroArch"**: Network Commands are off, or RetroArch uses another port.
- **"RetroArch couldn't read memory: no memory map defined"**: try another NES core.
- **"Model … isn't installed"**: run the `ollama pull` command it shows.
- **Mario doesn't move**: click the RetroArch window so it has keyboard focus, and check the default keyboard controls above.
- **"Memory is off"**: pull the embedding model, `ollama pull nomic-embed-text`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests use a fake game, a fake RetroArch and fake Ollama replies, so they don't need an emulator or a model.

## Ideas for what's next

- Add level layout (pipes, gaps and blocks) from the game's memory, so the model can see obstacles
- Give the model a screenshot with a vision model
- Fine-tune a small model on `decisions.jsonl`, keeping only the moves that went well
- Support other NES games with their own memory maps

## Project layout

```
mario_ai/
  __main__.py     start the dashboard and the AI (python -m mario_ai)
  agent.py        the play loop
  retroarch.py    RetroArch network commands
  game_state.py   Super Mario Bros. memory map and descriptions
  brain.py        move choice with Ollama structured outputs
  memory.py       retrieval-augmented memory with Ollama embeddings
  tracker.py      achievements and stats
  dashboard.py    web dashboard and controls
  templates/, static/
tests/
```

Memory addresses come from the [Data Crystal Super Mario Bros. RAM map](https://datacrystal.tcrf.net/wiki/Super_Mario_Bros./RAM_map). Super Mario Bros. is a trademark of Nintendo; this project isn't affiliated with Nintendo.

## Author

Created by [Jeremy Anderson](https://jeremyanderson.tech), MIT licensed.
