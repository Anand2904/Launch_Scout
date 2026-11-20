import queue
import threading
import time

import streamlit as st

from crew_events import set_queue
from crew_builder import run_launchscout
from flow_view import FLOW_CSS, new_state, apply_event, render_flow, render_trace
from report_style import REPORT_CSS

st.set_page_config(page_title="LaunchScout", page_icon="🔭", layout="wide")

# ---------- Styling: dark green with a glow ----------
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(900px 500px at 8% -10%, rgba(0,230,118,0.14), transparent 60%),
            radial-gradient(800px 500px at 100% 110%, rgba(0,200,130,0.10), transparent 60%),
            #04110a;
    }
    .block-container { padding-top: 1.2rem; padding-bottom: 1rem; max-width: 100%; }
    header[data-testid="stHeader"] { background: transparent; }

    /* Hero */
    .hero h1 {
        margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: .5px;
        background: linear-gradient(90deg, #b9ffd9, #00e676 45%, #69f0ae);
        -webkit-background-clip: text; background-clip: text; color: transparent;
        text-shadow: 0 0 24px rgba(0,230,118,.35);
    }
    .hero p { margin: .15rem 0 .8rem 0; color: #8fd9b0; font-size: .95rem; }

    /* Cards */
    div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid rgba(0,230,118,.28) !important;
        border-radius: 14px;
        background: rgba(11,35,22,.55);
        box-shadow: 0 0 22px rgba(0,230,118,.08), inset 0 0 18px rgba(0,230,118,.04);
    }

    /* Inputs */
    .stTextInput input, .stTextArea textarea {
        background: #07180f !important; border: 1px solid #14402a !important;
        color: #e8fff2 !important; border-radius: 10px;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #00e676 !important;
        box-shadow: 0 0 0 1px #00e676, 0 0 14px rgba(0,230,118,.45) !important;
    }
    label p { color: #9ff0c0 !important; font-weight: 600; font-size: .85rem; }

    /* Buttons */
    div[data-testid="stFormSubmitButton"] button, .stDownloadButton button {
        background: linear-gradient(135deg, #00e676, #00c853) !important;
        color: #03140a !important; font-weight: 700; border: none; border-radius: 10px;
        box-shadow: 0 0 16px rgba(0,230,118,.55);
        transition: all .2s ease;
    }
    div[data-testid="stFormSubmitButton"] button:hover, .stDownloadButton button:hover {
        box-shadow: 0 0 28px rgba(0,255,140,.9); transform: translateY(-1px);
    }

    /* How-it-works steps */
    .step {
        border: 1px solid rgba(0,230,118,.25); border-radius: 12px; padding: 14px;
        background: rgba(7,24,15,.7); height: 100%;
        box-shadow: 0 0 14px rgba(0,230,118,.07);
    }
    .step b { color: #00e676; text-shadow: 0 0 10px rgba(0,230,118,.5); }
    .step span { color: #9ccdb2; font-size: .85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Header ----------
st.markdown(
    """
    <div class="hero">
      <h1>🔭 LaunchScout</h1>
      <p>Four AI agents research your market and write a competitor report
      with prices, gaps and a launch plan.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Layout: form on the left, results on the right ----------
# ---------- Live run helpers ----------
def drain(q, state):
    while True:
        try:
            apply_event(state, q.get_nowait())
        except queue.Empty:
            break


def run_live(flow_ph, trace_ph, args):
    """Run the crew in a background thread and redraw the diagram as events arrive."""
    q = queue.Queue()
    set_queue(q)
    state = new_state()
    result = {}

    def worker():
        try:
            result["report"] = run_launchscout(*args)
        except Exception as e:  # shown in the UI
            result["error"] = str(e)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    def draw():
        flow_ph.markdown(render_flow(state), unsafe_allow_html=True)
        trace_ph.markdown(render_trace(state), unsafe_allow_html=True)

    while thread.is_alive():
        drain(q, state)
        draw()
        time.sleep(0.5)
    time.sleep(0.8)  # let the last events arrive
    drain(q, state)
    state["end"] = time.time()
    draw()
    return state, result


# ---------- Layout: form on the left, crew + report on the right ----------
st.markdown(f"<style>{FLOW_CSS}{REPORT_CSS}</style>", unsafe_allow_html=True)

left, right = st.columns([1, 2.4], gap="large")

with left:
    with st.form("idea_form"):
        business_idea = st.text_input(
            "Business idea", placeholder="Healthy millet meal box subscription"
        )
        c1, c2 = st.columns(2)
        city = c1.text_input("City", placeholder="Coimbatore")
        target_customer = c2.text_input(
            "Target customer", placeholder="Working professionals, 25-40"
        )
        known = st.text_area(
            "Known competitors (optional)", placeholder="One per line", height=80
        )
        submitted = st.form_submit_button(
            "🚀 Run research", type="primary", use_container_width=True
        )

with right:
    flow_ph = st.empty()    # the agent diagram
    trace_ph = st.empty()   # the live trace log
    state = st.session_state.get("flow_state") or new_state()

    valid = bool(business_idea.strip() and city.strip() and target_customer.strip())
    if submitted and not valid:
        st.error("Please fill in the business idea, city and target customer.")
    elif submitted:
        known_list = ", ".join(l.strip() for l in known.splitlines() if l.strip())
        state, result = run_live(
            flow_ph, trace_ph, (business_idea, city, target_customer, known_list)
        )
        st.session_state["flow_state"] = state
        if "error" in result:
            st.error(f"Something went wrong: {result['error']}")
        else:
            st.session_state["report"] = result["report"]

    # Always show the latest diagram and trace (also after a download click)
    flow_ph.markdown(render_flow(state), unsafe_allow_html=True)
    trace_ph.markdown(render_trace(state), unsafe_allow_html=True)

    # ---------- Report: full width, below the form and trace ----------
if "report" in st.session_state:
    title_col, dl_col = st.columns([8, 1], vertical_alignment="center")
    title_col.markdown('<div class="rep-title">📄 Your report</div>', unsafe_allow_html=True)
    dl_col.download_button(
        "⬇ Download .md",
        data=st.session_state["report"],
        file_name="launchscout_report.md",
        mime="text/markdown",
        key="dl_md",
    )
    with st.container(border=True, height=680, key="report"):
        st.markdown(st.session_state["report"])