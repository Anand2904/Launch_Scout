import html
import time

AGENTS = [
    {"role": "Market Researcher", "icon": "🔎", "color": "#00e676",
     "goal": "Finds real competitors, prices and sales channels",
     "tools": ["Serper", "Scraper"], "gets": None},
    {"role": "Review Analyst", "icon": "💬", "color": "#40e0d0",
     "goal": "Reads what customers like and complain about",
     "tools": ["Serper", "Scraper"], "gets": "Market Researcher"},
    {"role": "Strategy Analyst", "icon": "🧠", "color": "#c6ff00",
     "goal": "Builds the matrix, the gap and the price advice",
     "tools": [], "gets": "Researcher + Review Analyst"},
    {"role": "Report Writer", "icon": "📝", "color": "#69f0ae",
     "goal": "Writes the report and saves report.md",
     "tools": ["File writer"], "gets": "all three earlier tasks"},
]
ROLES = [a["role"] for a in AGENTS]
BY_ROLE = {a["role"]: a for a in AGENTS}

STATUS_TEXT = {"waiting": "Waiting", "working": "Working…", "done": "Done ✓"}


# ---------------------------------------------------------------- state
def new_state():
    return {
        "start": time.time(),
        "end": None,
        "agents": {r: {"status": "waiting", "tools": {}, "last": ""} for r in ROLES},
        "handoff": {r: None for r in ROLES},
        "log": [],
    }


def pretty_tool(name):
    n = (name or "").lower()
    if "serper" in n or "search" in n:
        return "Serper"
    if "scrape" in n or "website" in n:
        return "Scraper"
    if "file" in n or "writer" in n:
        return "File writer"
    return name or "tool"


def short(x, n=70):
    x = str(x).replace("\n", " ")
    x = x if len(x) <= n else x[: n - 1] + "…"
    return html.escape(x)


def apply_event(state, ev):
    role = ev["agent"]
    if role not in state["agents"]:
        return
    s = state["agents"][role]

    def log(text):
        state["log"].append({"t": ev["t"] - state["start"], "agent": role, "text": text})

    kind = ev["kind"]
    if kind == "task_start":
        s["status"] = "working"
        s["last"] = "Starting…"
        log("▶ started its task")
        gets = BY_ROLE[role]["gets"]
        if gets:
            log(f"📥 received context from {gets}")
    elif kind == "tool_start":
        name = pretty_tool(ev["tool"])
        s["tools"][name] = s["tools"].get(name, 0) + 1
        s["last"] = f"{name}: {short(ev['args'], 60)}"
        log(f"🔧 {name} · {short(ev['args'])}")
    elif kind == "tool_done":
        log(f"↩ {pretty_tool(ev['tool'])} returned {ev['chars']:,} chars")
    elif kind == "task_done":
        s["status"] = "done"
        s["last"] = f"Output: {ev['chars']:,} chars"
        state["handoff"][role] = ev["chars"]
        i = ROLES.index(role)
        tail = f" → handed to {ROLES[i + 1]}" if i + 1 < len(ROLES) else " → report ready"
        log(f"✔ finished ({ev['chars']:,} chars){tail}")


# ---------------------------------------------------------------- views
def _node(a, s):
    chips = "".join(
        f'<span class="chip {"on" if s["tools"].get(t) else ""}">{t}'
        f'{" ×" + str(s["tools"][t]) if s["tools"].get(t) else ""}</span>'
        for t in a["tools"]
    ) or '<span class="chip">no tools · reasons only</span>'
    return (
        f'<div class="node {s["status"]}" style="--c:{a["color"]}">'
        f'<div class="icon">{a["icon"]}</div>'
        f'<div class="role">{a["role"]}</div>'
        f'<div class="badge {s["status"]}">{STATUS_TEXT[s["status"]]}</div>'
        f'<div class="goal">{a["goal"]}</div>'
        f'<div class="chips">{chips}</div>'
        f'<div class="last">{s["last"] or "&nbsp;"}</div>'
        f"</div>"
    )


def _edge(state, up, down):
    u = state["agents"][up]["status"]
    d = state["agents"][down]["status"]
    cls = "flow" if (u == "done" and d == "working") else ("sent" if u == "done" else "idle")
    chars = state["handoff"][up]
    lbl = f"{chars / 1000:.1f}k chars" if chars else "output →"
    return f'<div class="edge {cls}"><div class="line"></div><div class="lbl">{lbl}</div></div>'


def render_flow(state):
    parts = ['<div class="flow">']
    for i, a in enumerate(AGENTS):
        parts.append(_node(a, state["agents"][a["role"]]))
        if i < len(AGENTS) - 1:
            parts.append(_edge(state, a["role"], AGENTS[i + 1]["role"]))
    parts.append("</div>")

    segs = ""
    for role, name in [("Market Researcher", "Research"),
                       ("Review Analyst", "Reviews"),
                       ("Strategy Analyst", "Strategy")]:
        on = state["agents"][role]["status"] == "done"
        segs += f'<span class="seg {"on" if on else ""}">{name}{" ✓" if on else ""}</span>'
    parts.append(
        '<div class="ctx"><span class="t">🗂 Shared context</span>'
        f"{segs}"
        '<span class="n">each task passes its output forward · the Writer reads all three</span>'
        "</div>"
    )
    return "".join(parts)


def render_trace(state):
    if not state["log"]:
        return ('<div class="trace"><div class="row">Agent trace will appear here '
                "as soon as you press Run research.</div></div>")
    end = state["end"] or time.time()
    secs = int(end - state["start"])
    head = f'<div class="row" style="color:#00e676">⏱ {secs // 60:02d}:{secs % 60:02d} · {len(state["log"])} events</div>'
    rows = []
    for e in reversed(state["log"][-80:]):
        a = BY_ROLE[e["agent"]]
        rows.append(
            f'<div class="row"><span class="ts">+{int(e["t"])}s</span>'
            f'<span class="ag" style="color:{a["color"]}">{a["icon"]} {a["role"]}</span>'
            f'{e["text"]}</div>'
        )
    return '<div class="trace">' + head + "".join(rows) + "</div>"


FLOW_CSS = """
.flow{display:grid;grid-template-columns:1fr 52px 1fr 52px 1fr 52px 1fr;align-items:stretch;margin:.2rem 0 .6rem 0}
.node{--c:#00e676;border:1px solid rgba(0,230,118,.25);border-radius:14px;padding:12px 10px;background:rgba(7,24,15,.78);transition:all .3s}
.node.waiting{opacity:.65}
.node.working{border-color:var(--c);opacity:1;animation:pulse 1.4s ease-in-out infinite}
.node.done{border-color:var(--c);opacity:1;box-shadow:0 0 12px var(--c)}
@keyframes pulse{0%,100%{box-shadow:0 0 8px var(--c)}50%{box-shadow:0 0 30px var(--c)}}
.node .icon{font-size:1.5rem}
.node .role{font-weight:700;color:#eafff3;font-size:.92rem;margin-top:2px}
.badge{display:inline-block;font-size:.7rem;padding:2px 9px;border-radius:99px;margin:5px 0;border:1px solid rgba(255,255,255,.14);color:#9ccdb2}
.badge.working{color:#03140a;background:var(--c);font-weight:700;border-color:var(--c)}
.badge.done{color:var(--c);border-color:var(--c)}
.goal{font-size:.74rem;color:#8fbfa5;line-height:1.25;min-height:2.5em}
.chips{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}
.chip{font-size:.68rem;padding:1px 7px;border-radius:8px;border:1px dashed #1f5a3b;color:#5f9a7b}
.chip.on{border-style:solid;border-color:var(--c);color:var(--c);box-shadow:0 0 8px var(--c)}
.last{font-size:.68rem;color:#7fb897;margin-top:6px;word-break:break-word;min-height:2.3em}
.edge{display:flex;flex-direction:column;align-items:center;justify-content:center}
.edge .line{position:relative;width:100%;height:3px;background:#12351f;border-radius:3px}
.edge .line::after{content:"";position:absolute;right:-2px;top:-4px;border-left:8px solid #12351f;border-top:5.5px solid transparent;border-bottom:5.5px solid transparent}
.edge.sent .line{background:#00e676;box-shadow:0 0 10px #00e676}
.edge.flow .line{background:linear-gradient(90deg,#0b2316 0%,#00e676 50%,#0b2316 100%);background-size:200% 100%;animation:flowx 1s linear infinite;box-shadow:0 0 12px #00e676}
.edge.sent .line::after,.edge.flow .line::after{border-left-color:#00e676}
@keyframes flowx{from{background-position:200% 0}to{background-position:-200% 0}}
.edge .lbl{font-size:.62rem;color:#7fd8a8;margin-top:6px;text-align:center}
.ctx{border:1px solid rgba(0,230,118,.25);border-radius:12px;padding:8px 12px;background:rgba(7,24,15,.6);display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:.6rem}
.ctx .t{color:#9ff0c0;font-weight:700;font-size:.8rem;margin-right:4px}
.ctx .n{font-size:.7rem;color:#6fae8c;margin-left:auto}
.seg{font-size:.72rem;padding:2px 10px;border-radius:8px;border:1px dashed #1f5a3b;color:#5f9a7b}
.seg.on{border-style:solid;border-color:#00e676;color:#b9ffd9;box-shadow:0 0 10px rgba(0,230,118,.6)}
.trace{max-height:210px;overflow-y:auto;border:1px solid rgba(0,230,118,.25);border-radius:12px;padding:8px 12px;background:rgba(3,14,8,.85);font-family:ui-monospace,Menlo,monospace;font-size:.74rem;line-height:1.6}
.trace .row{color:#bfe9d1}
.trace .ts{color:#4f8a6a;margin-right:8px}
.trace .ag{font-weight:700;margin-right:8px}
"""