"""Moment of GroundTruth: predict the cause of a gas pipeline incident from its narrative, and explain the project.

Run from the repository root::

    streamlit run app/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).parent
ROOT = APP_DIR.parent
sys.path.insert(0, str(APP_DIR))

st.set_page_config(page_title="Moment-of-GroundTruth", page_icon=str(ROOT / "docs" / "images" / "logo-stamp.png"), layout="centered")

RED = "#D8291F"
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
:root {{ --soil:#120e0b; --soil-2:#1c1611; --line:rgba(239,232,218,.17); --paper:#eee6d6; --ink:#1b1612;
        --text:#f1eadc; --mute:#d0c7b5; --stamp:{RED}; --gru:#e3a63a; --lstm:#5fa8ad; }}
html, body, [class*="css"], .stApp {{ font-family: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif; }}
.stApp {{ background: radial-gradient(120% 90% at 30% 0%, #1c1611, #120e0b 70%) fixed; color: var(--text); }}
header[data-testid="stHeader"] {{ background: transparent; }}
h1, h2, h3, .anton {{ font-family: 'Anton', 'Impact', 'Arial Narrow', sans-serif !important; letter-spacing: .012em; text-transform: uppercase; font-weight: 400 !important; color: var(--text); }}
h2 {{ color: var(--stamp); margin-top: 1.4rem; }}
h3 {{ margin-top: 1.1rem; }}
h5 {{ font-family: 'IBM Plex Mono', monospace !important; font-size: .85rem !important; letter-spacing: .14em; text-transform: uppercase; font-weight: 500 !important; color: var(--mute); margin-top: 1.4rem; display:flex; align-items:center; gap:.8rem; }}
h5::after {{ content:""; flex:none; width:2.2rem; height:1px; background: var(--line); }}
.block-container {{ max-width: 920px; padding-top: 1.6rem; }}
.title {{ font-family: 'Anton', 'Impact', sans-serif; color: var(--stamp); font-size: 3.6rem !important; line-height: .95 !important; letter-spacing: .015em; margin: 0; text-shadow: 0 .25rem 1.4rem rgba(0,0,0,.5); }}
.tag {{ color: var(--text); margin: .5rem 0 0 0; font-size: 1.1rem; line-height: 1.45; }}
.small {{ color: var(--mute); font-family: 'IBM Plex Mono', monospace; font-size: .8rem; letter-spacing: .03em; }}
.take {{ font-size: .95rem; border-left: 3px solid var(--stamp); padding-left: .8rem; margin-bottom: 1.6rem; color: var(--mute); }}
.stamp {{ display:inline-block; border: 5px solid var(--stamp); border-radius: 6px; padding: .35rem 1.1rem; transform: rotate(-4deg);
         color: var(--stamp); font-family:'Anton','Impact',sans-serif; font-size: 2.4rem; text-transform: uppercase; letter-spacing:.03em; line-height:1.15;
         filter: drop-shadow(0 .6rem 1rem rgba(0,0,0,.55)); }}
.stamp-wrap {{ padding: .3rem 0 .8rem .3rem; }}
.bar-row {{ display:flex; align-items:center; gap:.8rem; margin:.3rem 0; font-size:.95rem; }}
.bar-name {{ width: 15rem; flex: none; }}
.bar-track {{ flex:1; background: rgba(239,232,218,.07); height: 1.05rem; overflow:hidden; }}
.bar-fill {{ height: 100%; }}
.bar-pct {{ width: 3.4rem; text-align:right; font-family:'IBM Plex Mono',monospace; font-variant-numeric: tabular-nums; }}
.narr {{ line-height: 2.05; font-size: 1.02rem; background: var(--paper); color: var(--ink); padding: 1.1rem 1.3rem; box-shadow: 0 .8rem 2rem rgba(0,0,0,.45); }}
.narr span {{ padding: 2px 3px; border-radius: 2px; margin-right: 1px; }}
.legend span {{ display:inline-block; padding: 2px 8px; border-radius: 2px; margin-right: .5rem; font-family:'IBM Plex Mono',monospace; font-size:.78rem; color: var(--ink); }}
.card {{ border:1px solid var(--line); overflow:hidden; background: var(--soil-2); }}
.card .txt {{ padding: .9rem 1.1rem 1rem 1.1rem; }}
.noimg {{ height: 190px; display:flex; align-items:center; justify-content:center; background: var(--soil-2); color:var(--stamp); }}
.noimg-small {{ height: 120px; display:flex; align-items:center; justify-content:center; background: var(--soil-2); color:var(--stamp); font-size:.85rem; }}
.callout {{ background: var(--paper); color: var(--ink); border-left: 5px solid var(--stamp); padding: .8rem 1rem; margin: .7rem 0 1rem 0; box-shadow: 0 .6rem 1.6rem rgba(0,0,0,.4); }}
.callout b, .callout .small {{ color: var(--ink); }}
.stats {{ display:flex; gap:.8rem; flex-wrap:wrap; margin: .6rem 0 1rem 0; }}
.stat {{ flex:1; min-width: 8.5rem; background: var(--soil-2); border:1px solid var(--line); border-top: 3px solid var(--stamp); padding: .8rem .9rem; text-align:left; }}
.stat .num {{ font-family:'Anton','Impact',sans-serif; color:var(--text); font-size:2.2rem; line-height:1.05; font-variant-numeric: tabular-nums; }}
.stat .lab {{ font-family:'IBM Plex Mono',monospace; font-size:.74rem; letter-spacing:.1em; text-transform:uppercase; color: var(--mute); margin-top:.25rem; }}
.steps {{ display:flex; gap:.8rem; margin: .2rem 0 1rem 0; }}
.step {{ flex:1; background: var(--soil-2); border:1px solid var(--line); border-top: 2px solid var(--text); padding:.7rem .9rem; }}
.step .n {{ display:inline-block; width:1.7rem; height:1.7rem; border-radius:50%; background:var(--stamp); color:#fff; text-align:center; line-height:1.7rem; font-family:'IBM Plex Mono',monospace; font-weight:500; margin-bottom:.25rem; }}
button[data-baseweb="tab"] {{ font-family:'IBM Plex Mono',monospace; letter-spacing:.06em; text-transform: uppercase; font-size: .82rem; }}
div[data-baseweb="tab-list"] {{ border-bottom: 1px solid var(--line); }}
div.stButton > button[kind="primary"] {{ font-family:'Anton','Impact',sans-serif; letter-spacing:.06em; font-size:1.15rem; padding:.5rem 1.6rem; border-radius: 3px; text-transform: uppercase; box-shadow: 0 .4rem 1.2rem rgba(0,0,0,.45); }}
div.stButton > button:not([kind="primary"]) {{ font-family:'IBM Plex Mono',monospace; letter-spacing:.05em; border-radius:3px; border:1px solid var(--line); background: transparent; color: var(--text); }}
textarea {{ font-family:'IBM Plex Sans',sans-serif !important; background: var(--paper) !important; color: var(--ink) !important; }}
[data-testid="stTabs"] [data-testid="stImage"] img {{ box-shadow: 0 1rem 2.4rem rgba(0,0,0,.55); }}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_model():
    from explain import Classifier

    return Classifier()


# header
c1, c2 = st.columns([1, 4], vertical_alignment="center")
c1.image(str(ROOT / "docs" / "images" / "logo-stamp.png"), width=130)
c2.markdown(
    '<p class="title">MOMENT OF GROUNDTRUTH</p>'
    '<p class="tag">Every pipeline incident has a moment of truth. Paste a report and we dig down to the root cause.</p>',
    unsafe_allow_html=True,
)
st.write("")

# load the model once, before the user clicks anything, so the first answer is instant
if not (APP_DIR / "artifacts" / "head.pt").exists():
    st.error("The model file is missing. Run `python app/build_head.py` once to build it.")
    st.stop()
with st.spinner("Warming up the model (first visit only, about 10 seconds)..."):
    model = load_model()

import learn_tabs  # noqa: E402
import predict_tab  # noqa: E402

t_find, t_story, t_data, t_models, t_results, t_limits = st.tabs(
    ["Find the cause", "The story", "Data & split", "The models", "Results", "Limits & credits"]
)
with t_find:
    predict_tab.render(model)
with t_story:
    learn_tabs.story()
with t_data:
    learn_tabs.data_and_split()
with t_models:
    learn_tabs.models()
with t_results:
    learn_tabs.results()
with t_limits:
    learn_tabs.limits_and_credits()
