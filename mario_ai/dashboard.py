"""Local web dashboard: live state, decisions, stats, achievements and controls."""

import io
import os
import zipfile

from flask import Flask, Response, jsonify, render_template, request, send_file

from .retroarch import RetroArchError
from .tracker import ACHIEVEMENTS

CONTROLS = {
    "pause": "Paused the AI.",
    "resume": "Resumed the AI.",
    "reset": "Reset the game.",
    "save_state": "Saved a state.",
    "load_state": "Loaded the saved state.",
    "mark": "Marked a new episode.",
}


def create_app(agent):
    app = Flask(__name__)
    session = agent.session

    @app.get("/")
    def index():
        return render_template("dashboard.html", model=agent.config.model, achievements=list(ACHIEVEMENTS.items()))

    @app.get("/api/state")
    def state():
        since = request.args.get("since", default=0, type=int)
        data = session.snapshot(since)
        data["stats"] = agent.tracker.summary()
        data["model"] = agent.config.model
        return jsonify(data)

    @app.post("/api/control")
    def control():
        action = (request.get_json(silent=True) or {}).get("action")
        if action not in CONTROLS:
            return jsonify({"error": "Unknown control."}), 400
        try:
            if action == "pause":
                session.paused = True
            elif action == "resume":
                session.paused = False
            elif action == "reset":
                agent.retroarch.command("RESET")
            elif action == "save_state":
                agent.retroarch.command("SAVE_STATE")
            elif action == "load_state":
                agent.retroarch.command("LOAD_STATE")
        except (RetroArchError, OSError):
            return jsonify({"error": "Couldn't reach RetroArch."}), 502
        if action == "mark":
            with open(agent.decisions_path, "a", encoding="utf-8") as f:
                f.write('{"episode_mark": true}\n')
        session.event(CONTROLS[action], "control")
        return jsonify({"ok": True, "paused": session.paused})

    @app.get("/frame.jpg")
    def frame():
        if session.frame is None:
            return Response(status=204)
        return Response(session.frame, mimetype="image/jpeg", headers={"Cache-Control": "no-store"})

    @app.get("/api/export")
    def export():
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name in ("stats.json", "decisions.jsonl", "memory.jsonl"):
                path = os.path.join(agent.config.data_dir, name)
                if os.path.exists(path):
                    zf.write(path, name)
        buf.seek(0)
        return send_file(buf, mimetype="application/zip", as_attachment=True, download_name="mario-ai-session.zip")

    return app
