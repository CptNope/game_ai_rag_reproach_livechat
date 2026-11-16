"""Settings, all from environment variables."""

import os
from dataclasses import dataclass, field


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return default


@dataclass
class Config:
    retroarch_host: str = field(default_factory=lambda: os.getenv("RETROARCH_HOST", "127.0.0.1"))
    retroarch_port: int = field(default_factory=lambda: int(os.getenv("RETROARCH_PORT", "55355")))
    ollama_url: str = field(default_factory=lambda: os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/"))
    model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.2"))
    embed_model: str = field(default_factory=lambda: os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"))
    data_dir: str = field(default_factory=lambda: os.getenv("DATA_DIR", "game_memory"))
    # Seconds between decisions, and how long each move's keys are held.
    step_delay: float = field(default_factory=lambda: _float("STEP_DELAY", 0.2))
    hold_time: float = field(default_factory=lambda: _float("HOLD_TIME", 0.35))
    # Pause the emulator while the model thinks, so slow models still play fairly.
    think_paused: bool = field(default_factory=lambda: os.getenv("THINK_PAUSED", "1") == "1")
    # Capture the screen for the dashboard (needs the `mss` package and a display).
    capture_frames: bool = field(default_factory=lambda: os.getenv("CAPTURE_FRAMES", "0") == "1")
    dashboard_host: str = field(default_factory=lambda: os.getenv("HOST", "127.0.0.1"))
    dashboard_port: int = field(default_factory=lambda: int(os.getenv("PORT", "5000")))
