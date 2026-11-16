// Polls the agent once a second and redraws the dashboard. No outside libraries.
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const fmt = (n) => Number(n || 0).toLocaleString();
  let lastEvent = 0;
  let firstLoad = true;

  function text(id, value) { $(id).textContent = value; }

  function chart(svg, values) {
    const W = 600, H = 180, pad = 4;
    svg.replaceChildren();
    const ns = "http://www.w3.org/2000/svg";
    for (let i = 1; i < 4; i++) {
      const l = document.createElementNS(ns, "line");
      l.setAttribute("class", "grid-line");
      l.setAttribute("x1", 0); l.setAttribute("x2", W);
      l.setAttribute("y1", (H / 4) * i); l.setAttribute("y2", (H / 4) * i);
      svg.append(l);
    }
    if (values.length < 2) return;
    const min = Math.min(...values), max = Math.max(...values);
    const span = max - min || 1;
    const pts = values.map((v, i) => [
      (i / (values.length - 1)) * W,
      H - pad - ((v - min) / span) * (H - pad * 2),
    ]);
    const d = pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" ");
    const area = document.createElementNS(ns, "path");
    area.setAttribute("class", "area");
    area.setAttribute("d", d + " L" + W + " " + H + " L0 " + H + " Z");
    const line = document.createElementNS(ns, "path");
    line.setAttribute("class", "series");
    line.setAttribute("d", d);
    const label = document.createElementNS(ns, "text");
    label.setAttribute("x", 4); label.setAttribute("y", 12);
    label.textContent = fmt(max);
    svg.append(area, line, label);
  }

  function toast(label) {
    const t = document.createElement("div");
    t.className = "toast";
    const b = document.createElement("b");
    b.textContent = "Achievement unlocked";
    t.append(b, document.createTextNode(label));
    $("toasts").append(t);
    setTimeout(() => t.remove(), 6000);
  }

  function render(data) {
    const s = data.state;
    const st = data.stats;
    const dot = $("dot");
    if (data.problem) {
      dot.className = "dot bad";
      text("status", "Waiting: see the message below");
    } else if (data.paused) {
      dot.className = "dot paused";
      text("status", "AI paused · model " + data.model);
    } else {
      dot.className = s ? "dot ok" : "dot";
      text("status", s ? "Playing · model " + data.model + (data.memory_on ? " · memory on" : " · memory off") : "Connecting…");
    }
    $("problem").hidden = !data.problem;
    text("problem", data.problem || "");

    const toggle = $("toggle");
    toggle.dataset.action = data.paused ? "resume" : "pause";
    toggle.textContent = data.paused ? "Resume AI" : "Pause AI";

    if (s) {
      text("stage", s.stage);
      text("score", fmt(s.score));
      text("lives", s.lives);
    }
    if (data.situation) text("situation", data.situation);
    text("move", data.action ? data.action.replace(/_/g, " ") : "–");
    text("reason", data.reason || "");
    text("meta", data.think_ms ? "Decided in " + (data.think_ms / 1000).toFixed(1) + " s" : "");

    const mem = $("memories");
    mem.replaceChildren();
    if (!data.memories.length) {
      const li = document.createElement("li");
      li.className = "empty";
      li.textContent = data.memory_on ? "Nothing similar yet. Memories build up as it plays." : "Memory is off: pull the embedding model with `ollama pull nomic-embed-text`.";
      mem.append(li);
    }
    data.memories.forEach((m) => {
      const li = document.createElement("li");
      const b = document.createElement("b");
      b.textContent = m.action.replace(/_/g, " ");
      li.append(m.situation + " → ", b, ", " + m.outcome + ".");
      mem.append(li);
    });

    text("high", fmt(st.high_score));
    text("deaths", fmt(st.deaths));
    text("cleared", fmt(st.levels_cleared));
    text("run", fmt(st.longest_run) + " moves");

    chart($("x-chart"), data.x_series);
    chart($("score-chart"), data.score_series);

    const got = new Set(st.achievements.map((a) => a.key));
    const list = $("achievements");
    list.replaceChildren();
    window.ALL_ACHIEVEMENTS.forEach(([key, label]) => {
      const li = document.createElement("li");
      li.textContent = label;
      if (got.has(key)) li.className = "got";
      list.append(li);
    });
    text("ach-count", got.size + " of " + st.achievements_total);

    const levels = Object.keys(st.attempts).sort();
    const tbody = $("levels");
    if (levels.length) {
      tbody.replaceChildren(...levels.map((lv) => {
        const tr = document.createElement("tr");
        [lv, fmt(st.attempts[lv]), fmt(st.completions[lv] || 0), fmt(st.best_x[lv] || 0) + " px"].forEach((v) => {
          const td = document.createElement("td");
          td.textContent = v;
          tr.append(td);
        });
        return tr;
      }));
    }

    const events = $("events");
    data.events.forEach((e) => {
      const li = document.createElement("li");
      li.className = e.kind === "achievement" ? "achievement" : e.kind === "problem" ? "problem-ev" : "";
      const time = document.createElement("time");
      time.textContent = e.time;
      const span = document.createElement("span");
      span.textContent = e.text;
      li.append(time, span);
      events.prepend(li);
      if (e.kind === "achievement" && !firstLoad) toast(e.text.replace(/^Achievement: /, ""));
      lastEvent = Math.max(lastEvent, e.id);
    });
    while (events.children.length > 200) events.lastChild.remove();

    const panel = $("frame-panel");
    panel.hidden = !data.has_frame;
    if (data.has_frame) $("frame").src = "/frame.jpg?t=" + Date.now();
    firstLoad = false;
  }

  async function poll() {
    try {
      const res = await fetch("/api/state?since=" + lastEvent);
      if (res.ok) render(await res.json());
    } catch (err) {
      $("dot").className = "dot bad";
      text("status", "Can't reach the companion. Is it still running?");
    }
    setTimeout(poll, 1000);
  }

  document.querySelectorAll("[data-action]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      btn.disabled = true;
      try {
        const res = await fetch("/api/control", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ action: btn.dataset.action }),
        });
        const data = await res.json();
        if (!res.ok) text("status", data.error || "That didn't work.");
      } finally {
        btn.disabled = false;
      }
    });
  });

  poll();
})();
